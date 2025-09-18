import json
import urllib.parse
from threading import Thread

from pyxecm import OTCS


class GCdocs(OTCS):
    def create_folders(
        self,
        folder_path: list,
        workspace_id: int,
        translation_dict: dict | None = None
    ) -> int | None:
        parent_id = workspace_id
        child_id = None

        for folder_name in folder_path:
            response = self.check_node_name(
                parent_id=parent_id,
                node_name=folder_name
            )

            if response and 'results' in response and response['results']:
                child_id = int(response['results'][0]['id'])
            else:
                response = self.create_item(
                    parent_id=parent_id,
                    item_type=self.ITEM_TYPE_FOLDER,
                    item_name=folder_name
                )
                child_id = int(self.get_result_value(
                    response=response, key='id'
                ))

            if translation_dict and folder_name in translation_dict:
                name_multilingual = translation_dict[folder_name]
                self.rename_node(
                    node_id=child_id,
                    name=folder_name,
                    name_multilingual=name_multilingual
                )

            parent_id = child_id

        return child_id

    def remove_permission(
        self, node_id: int, assignee_type: str, assignee: int, apply_to: int = 0
    ) -> dict | None:
        if not assignee_type or assignee_type not in self.PERMISSION_ASSIGNEE_TYPES:
            self.logger.error(
                'Missing or wrong assignee type. Needs to be one of %s!',
                str(self.PERMISSION_ASSIGNEE_TYPES)
            )
            return None

        if assignee_type == 'custom' and not assignee:
            self.logger.error(
                'Assignee type is custom but permission assignee is missing!'
            )
            return None

        request_url = (
            self.config()['nodesUrlv2']
            + f'/{node_id}/permissions/{assignee_type}/{assignee}?apply_to={apply_to}'
        )
        request_header = self.request_form_header()

        return self.do_request(
            url=request_url,
            method='DELETE',
            headers=request_header,
            timeout=None,
            failure_message=f'Failed to remove assigned access permission with ID -> {assignee} for node with ID -> {node_id}'
        )

    def bulk_edit_custom_permissions(
        self,
        node_id: int,
        permissions: list[dict],
        apply_to: int = 0
    ) -> None:
        for permission in permissions:
            if permission['type'] == 'group':
                group = self.get_group(name=permission['name'])
                permission['id'] = self.get_result_value(
                    response=group, key='id')
            elif permission['type'] == 'user':
                user = self.get_user(name=permission['name'])
                permission['id'] = self.get_result_value(
                    response=user, key='id')
            elif permission['type'] == 'role':
                workspace_id = permission['workspace_id']
                roles = self.get_workspace_roles(workspace_id=workspace_id)
                names = self.get_result_values(response=roles, key='name')
                index = names.index(permission['name'])
                role_id = self.get_result_value(
                    response=roles, key='id', index=index)
                permission['id'] = role_id

            if permission['action'] == 'update':
                self.assign_permission(
                    node_id=node_id,
                    assignee_type='custom',
                    assignee=permission['id'],
                    permissions=permission['permissions'],
                    apply_to=apply_to
                )
            elif permission['action'] == 'remove':
                self.remove_permission(
                    node_id=node_id,
                    assignee_type='custom',
                    assignee=permission['id'],
                    apply_to=apply_to
                )

    def upgrade_categories(self, node_id: int, category_id: list) -> dict | None:
        request_url = (
            self.config()['nodesUrlv2'] + f'/{node_id}/categories/upgrade'
        )
        request_header = self.request_form_header()
        category_put_data = {'category_id': category_id}
        category_put_body = {'body': json.dumps(category_put_data)}

        return self.do_request(
            url=request_url,
            method='PUT',
            headers=request_header,
            data=category_put_body,
            timeout=None,
            failure_message=f'Failed to upgrade category with ID -> {category_id} on node with ID -> {node_id}'
        )

    def get_categories(self, node_id: int) -> dict | None:
        request_url = self.config()['nodesUrlv2'] + f'/{node_id}/categories'
        request_header = self.request_form_header()

        return self.do_request(
            url=request_url,
            method='GET',
            headers=request_header,
            timeout=None,
            failure_message=f'Failed to get categories on node with ID -> {node_id}'
        )

    def execute_parallel(
        self, root_id: int, task: callable, page_size: int = 25
    ) -> None:
        root = self.get_node(node_id=root_id)
        total_subnodes = self.get_result_value(response=root, key='size')
        total_pages = (total_subnodes + page_size - 1) // page_size

        for page in range(1, total_pages + 1):
            print('page', page)
            nodes = self.get_subnodes(
                parent_node_id=root_id,
                filter_node_types=self.ITEM_TYPE_BUSINESS_WORKSPACE,
                limit=page_size,
                page=page
            )
            node_ids = self.get_result_values(response=nodes, key='id')
            threads = [
                Thread(target=task, args=(node_id,))
                for node_id in node_ids
            ]

            for t in threads:
                t.start()

            for t in threads:
                t.join()

    def clear_workspace_roles(self, workspace_id: int) -> None:
        roles = self.get_workspace_roles(workspace_id=workspace_id)

        if roles and roles['results']:
            roles = self.get_result_values(response=roles, key='id')
            for role_id in roles:
                self.remove_permission(
                    node_id=workspace_id, assignee_type='custom', assignee=role_id
                )

    def delete_node_by_name(self, parent_id: int, name: str) -> dict | None:
        response = self.check_node_name(
            parent_id=parent_id,
            node_name=name
        )

        if response and 'results' in response and response['results']:
            node_id = response['results'][0]['id']
            return self.delete_node(node_id)

    def get_group_ids_from_names(self, group_names: list) -> dict:
        group_ids = {}

        for group_name in group_names:
            group = self.get_group(name=group_name)
            group_id = self.get_result_value(response=group, key='id')
            group_ids[group_name] = group_id

        return group_ids

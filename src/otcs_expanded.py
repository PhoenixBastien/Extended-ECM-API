import urllib.parse

from pyxecm import OTCS


def create_folders(
    otcs: OTCS,
    relative_path: str,
    workspace_id: int,
    translation_dict: dict | None = None
) -> int:
    parent_id = workspace_id

    for folder_name in relative_path.split(':'):
        response = otcs.check_node_name(
            parent_id=parent_id,
            node_name=folder_name
        )

        if not response:
            continue

        if response['results']:
            child_id = response['results'][0]['id']
        else:
            response = otcs.create_item(
                parent_id=parent_id,
                item_type=OTCS.ITEM_TYPE_FOLDER,
                item_name=folder_name
            )
            child_id = otcs.get_result_value(response=response, key='id')

        if translation_dict and folder_name in translation_dict:
            name_multilingual = translation_dict[folder_name]
            otcs.rename_node(
                node_id=child_id,
                name=folder_name,
                description='',
                name_multilingual=name_multilingual
            )

        parent_id = child_id

    return child_id

def remove_custom_permission(
    otcs: OTCS, node_id: int, assignee: int, apply_to: int = 0
) -> dict | None:
    query = {'apply_to': apply_to}
    encoded_query = urllib.parse.urlencode(query=query, doseq=True)

    request_url = (
        otcs.config()['nodesUrlv2']
        + f'/{node_id}/permissions/custom/{assignee}?{encoded_query}'
    )

    request_header = otcs.request_form_header()

    return otcs.do_request(
        url=request_url,
        method='DELETE',
        headers=request_header,
        timeout=None,
        failure_message=f'Failed to remove assigned access permission with ID -> {assignee} for node with ID -> {node_id}'
    )

def bulk_edit_custom_permissions(
    otcs: OTCS,
    node_id: int,
    permissions: list[dict],
    apply_to: int = 0
) -> None:
    for permission in permissions:
        if permission['type'] == 'group':
            group = otcs.get_group(permission['name'])
            permission['id'] = otcs.get_result_value(response=group, key='id')
        elif permission['type'] == 'user':
            user = otcs.get_user(permission['name'])
            permission['id'] = otcs.get_result_value(response=user, key='id')
        elif permission['type'] == 'role':
            roles = otcs.get_workspace_roles(permission['workspace_id'])
            names = otcs.get_result_values(response=roles, key='name')
            index = names.index(permission['name'])
            permission['id'] = otcs.get_result_value(
                response=roles, key='id', index=index
            )

        if permission['action'] == 'update':
            otcs.assign_permission(
                node_id=node_id,
                assignee_type='custom',
                assignee=permission['id'],
                permissions=permission['permissions'],
                apply_to=apply_to
            )
        elif permission['action'] == 'remove':
            remove_custom_permission(
                otcs,
                node_id=node_id,
                assignee=permission['id'],
                apply_to=apply_to
            )
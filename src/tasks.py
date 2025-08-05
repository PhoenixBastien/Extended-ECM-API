from otcs_expanded import *

def task(otcs: OTCS, workspace_id: int) -> None:
    # dict of french translations of node names
    translation_dict = {
        'Payments/Monitoring': {
            'en': 'Payments/Monitoring',
            'en_CA': 'Payments/Monitoring',
            'fr_CA': 'Paiements/surveillance'
        },
        'Payment Packages': {
            'en': 'Payment Packages',
            'en_CA': 'Payment Packages',
            'fr_CA': 'Paquets de paiement'
        },
        'Close-out': {
            'en': 'Close-out',
            'en_CA': 'Close-out',
            'fr_CA': 'Clôture'
        }
    }

    # create folders
    payment_packages_id = create_folders(
        otcs,
        relative_path='Payments/Monitoring:Payment Packages',
        workspace_id=workspace_id,
        translation_dict=translation_dict
    )

    # edit permissions
    payment_packages_permissions = [
        {
            'name': 'CMB-CIOD-IMDD - Records Office | SGM-DGDPR-DGID - Bureau des archives',
            'permissions': [
                'see',
                'see_contents',
                'modify',
                'edit_attributes',
                'add_items',
                'reserve',
                'add_major_version',
                'delete_versions',
                'delete',
                'edit_permissions'
            ],
            'type': 'group',
            'action': 'update'
        },
        {
            'name': 'Financial Operations Group | Groupe des Opérations financières',
            'permissions': [
                'see',
                'see_contents'
            ],
            'type': 'group',
            'action': 'update'
        },
        {
            'name': 'PS-ALL',
            'workspace_id': workspace_id,
            'type': 'role',
            'action': 'remove'
        },
        {
            'name': 'Record.Office',
            'workspace_id': workspace_id,
            'type': 'role',
            'action': 'remove'
        },
        {
            'name': 'PS-All | SP-Tout',
            'type': 'group',
            'action': 'remove'
        }
    ]

    bulk_edit_custom_permissions(
        otcs,
        node_id=payment_packages_id,
        permissions=payment_packages_permissions,
        apply_to=2
    )

    # create folders
    close_out_id = create_folders(
        otcs,
        relative_path='Close-out',
        workspace_id=workspace_id,
        translation_dict=translation_dict
    )

    # edit permissions
    close_out_permissions = [
        {
            'name': 'PS-ALL',
            'workspace_id': workspace_id,
            'permissions': [
                'see',
                'see_contents',
                'modify',
                'edit_attributes',
                'add_items',
                'reserve',
                'add_major_version',
                'delete_versions',
                'delete',
                'edit_permissions'
            ],
            'type': 'role',
            'action': 'update'
        }
    ]

    bulk_edit_custom_permissions(
        otcs,
        node_id=close_out_id,
        permissions=close_out_permissions,
        apply_to=2
    )

def task2(otcs: OTCS, workspace_id: int) -> None:
    response = otcs.check_node_name(
        parent_id=workspace_id,
        node_name='Close-Out'
    )

    if response and response['results']:
        node_id = response['results'][0]['id']
        otcs.delete_node(node_id)
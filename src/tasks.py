from gcdocs import GCdocs


def grants_and_contributions(gcdocs: GCdocs, workspace_id: int) -> None:
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
        'Close-out': {'en': 'Close-out', 'en_CA': 'Close-out', 'fr_CA': 'Clôture'}
    }

    # create payments/monitoring and payment packages folders
    payment_packages_id = gcdocs.create_folders(
        relative_path='Payments/Monitoring:Payment Packages',
        workspace_id=workspace_id,
        translation_dict=translation_dict
    )

    # edit payment packages folder permissions
    payment_packages_permissions = [
        {
            'name': 'CMB-CIOD-IMDD - Records Office | SGM-DGDPR-DGID - Bureau des archives',
            'permissions': GCdocs.PERMISSION_TYPES,
            'type': 'group',
            'action': 'update'
        },
        {
            'name': 'Financial Operations Group | Groupe des Opérations financières',
            'permissions': GCdocs.PERMISSION_TYPES[:2],
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
        {'name': 'PS-All | SP-Tout', 'type': 'group', 'action': 'remove'}
    ]

    gcdocs.bulk_edit_custom_permissions(
        node_id=payment_packages_id,
        permissions=payment_packages_permissions,
        apply_to=2
    )

    # create close-out folder
    close_out_id = gcdocs.create_folders(
        relative_path='Close-out',
        workspace_id=workspace_id,
        translation_dict=translation_dict
    )

    # edit close-out folder permissions
    close_out_permissions = [
        {
            'name': 'PS-ALL',
            'workspace_id': workspace_id,
            'permissions': GCdocs.PERMISSION_TYPES,
            'type': 'role',
            'action': 'update',
        }
    ]

    gcdocs.bulk_edit_custom_permissions(
        node_id=close_out_id, permissions=close_out_permissions, apply_to=2
    )

    # delete duplicate close-out folder
    gcdocs.delete_node_by_name(parent_id=workspace_id, name='Close-Out')


def assign_workspace_permissions(gcdocs: GCdocs, workspace_id: int) -> None:
    assignees = [
        78209,
        30665104,
        30665384,
        30665444,
        30665659,
        30716420,
        30716726,
        40359816,
        46040346,
        51315755
    ]

    for assignee in assignees:
        gcdocs.assign_permission(
            node_id=workspace_id,
            permissions=GCdocs.PERMISSION_TYPES[:2],
            assignee_type='custom',
            assignee=assignee
        )


def assign_subfolder_permissions(gcdocs: GCdocs, workspace_id: int) -> None:
    subfolders = [
        {'name': 'AWARDS AND RECOGNITION', 'assignees': [30716726]},
        {'name': 'COMPENSATION', 'assignees': [30665444, 40359816]},
        {'name': 'CONFLICT OF INTEREST', 'assignees': [30665659]},
        {'name': 'DUTY TO ACCOMMODATE', 'assignees': [51315755]},
        {'name': 'EX PROGRAMS', 'assignees': [30716420, 30665444]},
        {'name': 'LABOUR RELATIONS', 'assignees': [30665384]},
        {'name': 'LEARNING AND DEVELOPMENT', 'assignees': [30716726]},
        {'name': 'OCCUPATIONAL HEALTH AND SAFETY', 'assignees': [78209]},
        {'name': 'STAFFING', 'assignees': [30665104, 30665444]}
    ]

    for node in subfolders:
        node_name = node['name']
        assignees = node['assignees']
        response = gcdocs.check_node_name(
            parent_id=workspace_id, node_name=node_name
        )

        if response and 'results' in response and response['results']:
            node_id = response['results'][0]['id']
        else:
            response = gcdocs.create_item(
                parent_id=workspace_id,
                item_type=GCdocs.ITEM_TYPE_FOLDER,
                item_name=node_name
            )
            node_id = gcdocs.get_result_value(response=response, key='id')

        for assignee in assignees:
            response = gcdocs.assign_permission(
                node_id=node_id,
                permissions=GCdocs.PERMISSION_TYPES[:6],
                assignee_type='custom',
                assignee=assignee,
                apply_to=2
            )


def personnel_records(gcdocs: GCdocs, workspaced_id: int) -> None:
    gcdocs.clear_workspace_roles(workspace_id=workspaced_id)
    assign_workspace_permissions(gcdocs=gcdocs, workspace_id=workspaced_id)
    assign_subfolder_permissions(gcdocs=gcdocs, workspace_id=workspaced_id)

# {
#     'CMB-PCD-DID - Duty to Accommodate (DTA) | SGM-DGPC-DDI - Obligation de prendre des mesures d’adaptation (OPMA)':                51315755,
#     'CMB-PCD-CPD - Learning & Development | SGM-DGPC-DPM - Apprentissage et perfectionnement':                                       30716726,
#     'CMB-PCD-CPD – Values, Inclusion, Ethics and Wellness (VIEW) | SGM-DGPC-DPM - Valeurs, Inclusion, Éthique et Bien-Être (VIEM)':  30665659,
#     'CMB-PCD-EPCSD - Client Services (Staffing) | SGM-DGPC-DPCDSC - Service clientèle (Dotation)':                                   30665104,
#     'CMB-PCD-EPCSD - Executive (EX) Programs and Staffing | SGM-DGPC-DPCDSC - Programmes aux cadres supérieurs et recrutement (CS)': 30716420,
#     'CMB-PCD-LRWD - Labour Relations Operations | SGM-DGPC-DRTB - Opérations des relations de travail':                              30665384,
#     'CMB-PCD-LRWD - Values and Ethics | SGM-DGPC-DRTB - Valeurs et Éthique':                                                         46040346,
#     'CMB-PCD-LRWD | SGM-DGPC-DRTB':                                                                                                  78209,
#     'CMB-PCD-PAHRPCD - HR Trusted Source | SGM-DGPC-DAPPRHR - Source Fiable de RH':                                                  30665444,
#     'HR.HRTS':                                                                                                                       40359816
# }

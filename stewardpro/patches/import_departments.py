import frappe

departments = [
    {"doctype": "Department", "department_name": "Shule ya Sabato", "department_code": "SS", "is_active": 1, "description": "Inashughulikia programu na shughuli za Shule ya Sabato."},

    # Idara ya Vijana
    {"doctype": "Department", "department_name": "Idara ya Vijana", "department_code": "YM", "is_active": 1, "description": "Inalenga ushiriki wa vijana na ukuaji wa kiroho."},
    {"doctype": "Department", "department_name": "Pathfinder", "department_code": "PF", "parent_department": "Idara ya Vijana", "is_active": 1, "description": "Inalea vijana kupitia mafunzo ya uongozi, ustadi, na Idara."},
    {"doctype": "Department", "department_name": "Adventurer", "department_code": "AD", "parent_department": "Idara ya Vijana", "is_active": 1, "description": "Inakuza ukuaji wa watoto kupitia mafundisho na shughuli za maendeleo."},
    {"doctype": "Department", "department_name": "Ambassador", "department_code": "AMB", "parent_department": "Idara ya Vijana", "is_active": 1, "description": "Inahudumia vijana balehe na kuandaa viongozi wa baadaye."},
    {"doctype": "Department", "department_name": "Young Adults", "department_code": "YA", "parent_department": "Idara ya Vijana", "is_active": 1, "description": "Inawaunganisha vijana watu wazima katika Idara na ukuaji wa kiroho."},

    {"doctype": "Department", "department_name": "Idara ya Watoto", "department_code": "CM", "is_active": 1, "description": "Inatoa Idara kwa mahitaji ya kiroho na kijamii ya watoto."},

    {"doctype": "Department", "department_name": "Idara ya Muziki", "department_code": "MM", "is_active": 1, "description": "Inaangalia shughuli za muziki na ibada."},

    {"doctype": "Department", "department_name": "Idara za Jamii", "department_code": "CS", "is_active": 1, "description": "Inaendesha miradi ya Idara na msaada kwa jamii."},

    {"doctype": "Department", "department_name": "Idara ya Wanawake", "department_code": "WM", "is_active": 1, "description": "Inasaidia ukuaji wa kiroho na kijamii wa wanawake."},

    {"doctype": "Department", "department_name": "Idara ya Wanaume", "department_code": "MEN", "is_active": 1, "description": "Inawezesha wanaume katika shughuli za kanisa na jamii."},

    {"doctype": "Department", "department_name": "Idara ya Afya", "department_code": "HM", "is_active": 1, "description": "Inapromoti programu za afya na ustawi wa kanisa na jamii."},

    {"doctype": "Department", "department_name": "Idara ya Elimu", "department_code": "EDU", "is_active": 1, "description": "Inasimamia miradi na programu za elimu."},

    {"doctype": "Department", "department_name": "Huduma", "department_code": "EV", "is_active": 1, "description": "Inaongoza shughuli za uinjilisti na misioni."},

    {"doctype": "Department", "department_name": "Uwakili", "department_code": "ST", "is_active": 1, "description": "Inahimiza uaminifu katika utoaji na usimamizi wa mali ya Mungu."},

    {"doctype": "Department", "department_name": "Kaya na Familia", "department_code": "FL", "is_active": 1, "description": "Inaleta mafundisho na msaada kwa familia."},

    {"doctype": "Department", "department_name": "Mawasiliano", "department_code": "COM", "is_active": 1, "description": "Inashughulikia mawasiliano ya kanisa na media."},

    {"doctype": "Department", "department_name": "Ofisi ya Wazee", "department_code": "GEN", "is_active": 1, "description": "Usimamizi wa jumla wa shughuli za kanisa."},
    # Children’s Ministries
    {"doctype": "Department", "department_name": "Idara ya Watoto", "department_code": "CM", "is_active": 1, "description": "Inatoa Idara kwa mahitaji ya kiroho na kijamii ya watoto."},

    # Women’s Ministries
    {"doctype": "Department", "department_name": "Idara ya Wanawake", "department_code": "WM", "is_active": 1, "description": "Inasaidia ukuaji wa kiroho na kijamii wa wanawake."},

    # Men’s Ministries
    {"doctype": "Department", "department_name": "Idara ya Wanaume", "department_code": "MEN", "is_active": 1, "description": "Inawezesha wanaume katika shughuli za kanisa na jamii."},

    # Deacons & Deaconesses
    {"doctype": "Department", "department_name": "Mashemasi", "department_code": "DCN", "is_active": 1, "description": "Wanahusika na ibada, matambiko na Idara za kusaidia kanisani."},

    # Publishing / Literature
    {"doctype": "Department", "department_name": "Uchapishaji", "department_code": "PUB", "is_active": 1, "description": "Inaratibu Idara ya vitabu na uchapishaji kwa ajili ya uinjilisti."},

    # Church Development / Building Committee
    {"doctype": "Department", "department_name": "Majengo", "department_code": "DEV", "is_active": 1, "description": "Inasimamia miradi ya ujenzi na maendeleo ya miundombinu ya kanisa."},
]

def execute():
    for dept in departments:
        if not frappe.db.exists('Department', dept['department_name']):
            doc = frappe.get_doc(dept)
            doc.insert(ignore_permissions=True)
        else:
            continue
    frappe.db.commit()
    print("Department creation completed!")

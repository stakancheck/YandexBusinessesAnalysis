import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from neo4j import GraphDatabase, basic_auth
import nxneo4j as nx

driver = GraphDatabase.driver(uri="neo4j+s://d40ca650.databases.neo4j.io",
                              auth=('neo4j', 'ku0LsPxtBFgYec-jm0D5k_gTv6ZsLl9mzFCTNKdpBtU'))
G = nx.Graph(driver)
df = pd.read_csv('database.csv')
#G.delete_all()
for i in df[:50].values:
    G.node_label = 'URL'
    G.add_node(i[0])
    if i[1] != 'None':
        G.relationship_type = 'Name_Of_Organization'
        G.add_edge(i[0], i[1])
    if i[2] != 'None':
        for phone in i[2].split('&'):
            G.relationship_type = 'Phone_Number'
            G.add_edge(i[0], phone)
    if i[3] != 'None':
        for email in i[3].split('&'):
            G.relationship_type = 'Email'
            G.add_edge(i[0], email)
    if i[4] != 'None':
        G.relationship_type = 'General_Director'
        G.add_edge(i[0], i[4])
    if i[6] != 'None':
        G.relationship_type = 'Registration_Date'
        G.add_edge(i[0], i[6])
    if i[8] != 'None':
        for founder in i[8].split('&'):
            G.relationship_type = 'Founder'
            G.add_edge(i[0], founder)
    if i[9] != 'None':
        G.relationship_type = 'INN'
        G.add_edge(i[0], i[9])
    if i[10] != 'None':
        G.relationship_type = 'OGRN'
        G.add_edge(i[0], i[10])
    if i[11] != 'None':
        G.relationship_type = 'KPP'
        G.add_edge(i[0], i[11])
    if i[12] != 'None':
        G.relationship_type = 'OKPO'
        G.add_edge(i[0], i[12])
    if i[13] != 'None':
        G.relationship_type = 'OKATO'
        G.add_edge(i[0], i[13])
    if i[14] != 'None':
        G.relationship_type = 'OKTMO'
        G.add_edge(i[0], i[14])
    if i[16] != 'None':
        G.relationship_type = 'POSTAL_CODE'
        G.add_edge(i[0], i[16])
    if i[17] != 'None':
        G.relationship_type = 'Address'
        G.add_edge(i[0], i[17])

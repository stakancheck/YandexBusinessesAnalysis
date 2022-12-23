import numpy as np
import scipy as sp
import pandas as pd
import nxneo4j as nx
import matplotlib.pyplot as plt

from pathlib import Path
from neo4j import GraphDatabase, basic_auth


PROJECT_DIR = str(Path(__file__).parent.parent.parent)


def main():
    driver = GraphDatabase.driver(uri="neo4j+s://d40ca650.databases.neo4j.io",
                                  auth=('neo4j', 'ku0LsPxtBFgYec-jm0D5k_gTv6ZsLl9mzFCTNKdpBtU'))
    G = nx.Graph(driver)
    df = pd.read_csv(PROJECT_DIR + '/database.csv')

    # G.delete_all()

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
            for date in i[6].split('&'):
                if date != 'None':
                    G.relationship_type = 'Registration_Date'
                    G.add_edge(i[0], date)
        if i[8] != 'None':
            for founder in i[8].split('&'):
                if founder != 'None':
                    G.relationship_type = 'Founder'
                    G.add_edge(i[0], founder)
        if i[9] != 'None':
            for type_org in i[9].split('&'):
                if type_org != 'None':
                    G.relationship_type = 'INN'
                    G.add_edge(i[0], type_org)
        if i[10] != 'None':
            for ogrn in i[10].split('&'):
                if ogrn != 'None':
                    G.relationship_type = 'OGRN'
                    G.add_edge(i[0], ogrn)
        if i[11] != 'None':
            for kpp in i[11].split('&'):
                if kpp != 'None':
                    G.relationship_type = 'KPP'
                    G.add_edge(i[0], kpp)
        if i[12] != 'None':
            for okpo in i[12].split('&'):
                if okpo != 'None':
                    G.relationship_type = 'OKPO'
                    G.add_edge(i[0], okpo)
        if i[13] != 'None':
            for okato in i[13].split('&'):
                if okato != 'None':
                    G.relationship_type = 'OKATO'
                    G.add_edge(i[0], okato)
        if i[14] != 'None':
            for oktmo in i[14].split('&'):
                if oktmo != 'None':
                    G.relationship_type = 'OKTMO'
                    G.add_edge(i[0], oktmo)
        if i[16] != 'None':
            for code in i[16].split('&'):
                if code != 'None':
                    G.relationship_type = 'POSTAL_CODE'
                    G.add_edge(i[0], code)
        if i[17] != 'None':
            for addr in i[17].split('&'):
                if addr != 'None':
                    G.relationship_type = 'Address'
                    G.add_edge(i[0], addr)


if __name__ == '__main__':
    main()

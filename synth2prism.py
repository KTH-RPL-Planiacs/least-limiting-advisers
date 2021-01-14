def synth2prism(synth):
    name = synth.graph['name']
    prod_mdp_nm_file = open("data/%s_2prism.prism" % name, "w")

    prod_mdp_nm_file.write('//synthesis game in PRISM-games language, generated from networkx digraph model \n')
    prod_mdp_nm_file.write('\n')

    prod_mdp_nm_file.write('smg \n')
    prod_mdp_nm_file.write('\n')
    prod_mdp_nm_file.write('\n')

    #player blocks

    #

    return None


if __name__ == '__main__':
    pass

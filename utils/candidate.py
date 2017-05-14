import re

class Candidate():
    def __init__(self, name):

        self.name = name.capitalize()

        if name == 'LEPEN':
            self.ids = 'MLP, MLP2017, @MLP_officiel, MLP_officiel, Marine2017, lepen2017, LePen, Le Pen, AuNomDuPeuple, FN'.split(', ')
        elif name == 'MACRON':
            self.ids = 'Macron, enmarche, #EmmanuelMacron, Macron2017, @EmmanuelMacron, EmmanuelMacron'.split(', ')
        elif name == 'HAMON':
            self.ids = '@benoithammon, benoithammon, Hamon, ProjetBH, Hamon2017, AvecHamon'.split(', ')
        elif name == 'MELENCHON':
            self.ids = '@JLMelenchon, JLMelenchon, JLM, jlm2017.fr, FranceInsoumise, France Insoumise, JLM2017, Mélenchon, Melenchon, Melenchon2017'.split(', ')
        elif name == 'FILLON':
            self.ids = '@Fillon2017_fr, Fillon2017_fr, FF2017, Francois Fillon, François Fillon, FillonPresident, Fillon, @FrancoisFillon, FrancoisFillon, Fillon2017'.split(', ')
        elif name == 'POUTOU':
            self.ids = '@PhilippePoutou, PhilippePoutou, Poutou2017, Philippe Poutou, P. Poutou, Poutou'.split(', ')
        elif name == 'ASSELINEAU':
            self.ids ='@UPR_Asselineau, UPR_Asselineau, Asselineau, @Fasselineau, Fasselineau'.split(', ')
        elif name == 'DUPONT':
            self.ids = '@dupontaignan, dupontaignan, NDA2017, Dupont-Aignan, Dupont Aignan'.split(', ')
        elif name == 'ARTHAUD':
            self.ids = '@n_arthaud, n_arthaud, Arthaud, Arthaud2017'.split(', ')
        elif name == 'CHEMINADE':
            self.ids ='@JCheminade, JCheminade, Cheminade2017, cheminade2017.fr, Cheminade'.split(', ')
        elif name == 'LASSALLE':
            self.ids = 'Jean Lassalle, Lassalle, Lassalle2017, jeanlassalle2017.fr'.split(', ')
        else:
            print('Unrecognized candidate name')

        self.popularity = {}

    def regex(self):
        return re.compile(r'(?:%s)' % '|'.join(self.ids), re.IGNORECASE)

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

Nous avons implémenté  tous les modèles demandés, et 6 instances de tailles respective 5, 10, 100, 1000, ..., 100000 de facon aléatoire.
Nous avons également rajouté des contraintes sur les yi (du type yi >= yj) afin de reproduire un modèle similaire a celui de l'exemple sur les slides.
La version de CPLEX utilisée pour les tests est  : CPLEX 22.1.1.0, et les temps comparés sont les temps de résolution des modèles,
sans compter les temps de création des modèles. A noter que le Benders automatique ne fonctionnait pas en rajoutant
les contraintes yi >= yj. Voici les résultats :
On note I0, I1, ..., I5 les instances, de taille respectives 5, 10, 100, 1000, ..., 100000 
Sans les contraintes yi>=yj, les temps de calcul sont (en secondes) :
        Sans decomp     Decomp avec PL      Decomp sans PL      Decomp auto
I0      0.00099         0.00998             0.01258             0.00699  
I1      0.00100         0.00383             0.00357             0.00399
I2      0.00001         0.01523             0.01212             0.00010
I3      0.00900         0.07747             0.07832             0.00500
I4      0.06800         1.00108             0.70814             0.01600
I5      1.69699         8.75251             8.66295             0.13899

Avec les contraintes yi>=yj (rajoutées aléatoirement), on obtient les temps de calcul suivants :

        Sans decomp     Decomp avec PL      Decomp sans PL
I0      0.00399         0.00941             0.00476 
I1      0.00001         0.00315             0.00596
I2      0.00300         0.01454             0.01518
I3      0.00001         0.07217             0.08218
I4      0.05400         0.87120             0.80918
I5      0.31000         8.26259             8.73963

Nous pouvons remarquer que :
-Sans les contraintes yi >= yj, la méthode directe parait plus efficace que la décomposition de Benders faite a la main, avec ou sans PL.
Le cout de résoudre les problèmes maitres/de separation est trop important ici.
-Il est a noter que la séparation automatique faite avec CPLEX et très efficace, et
résout tous les problèmes bien plus rapidement (jusqu'à un facteur presque 10)

- Avec les contraintes yi >= yj, on remarque le même phénomène :  utiliser la décomposition de Benders (avec ou sans PL)
augmente toujours le temps de résolution pour ces instance. Il y a plus d'un facteur 10 aussi pour la dernière instance.
Il est donc toujours trop couteux de rajouter les coupes à la main et de résoudre les sous-problèmes.



Dans les deux cas, la décomposition manuelle pour ces instances 
de ce problème ne vaut pas la chandelle, et ralentit même fortement
la résolution pour la plus grande instance. L'approche frontale
serait donc la plus appropriée ici par rapport à la décomposition à la main (avec ou sans PL).
La décomposition automatique de CPLEX semble ici encore plus efficace, donc peut être testée, mais ne fonctionne pas
en rajoutant les contraintes yi >= yj, donc s'applique potentiellement à moins d'instances de problèmes.


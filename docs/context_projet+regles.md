Contexte du projet
 Le projet s’articule autour de l’utilisation des nouvelles technologies d’IA Générative (Ge
nAi) afin de faciliter les revues effectuées par l’équipe Compliance sur les documents émis par le
 Marketing d’un acteur de l’Asset Management.
 Comme précisé dans le schéma de présentation, une approche “Human in the loop” sera mise en
 place pour permettre à la Compliance d’intervenir dans la correction des documents. Dans ce cadre, la
 partie la plus importante de l’exercice consiste à annoter chaque document en précisant la règle
 qui a été enfreinte.
 Objectif général
 L’objectif du projet est de proposer une solution technique d’automatisation du contrôle
 de conformité marketing, en s’appuyant sur le corpus de règles fourni. Chaque équipe d’étudiants
 devra déterminer :
 — la méthode d’analyse du texte ou des documents,
 — les technologies d’IA Générative à utiliser,
 — et la manière d’intégrer les règles de conformité à leur solution.
 Corpus de règles
 Le corpus de règles a été rédigé spécifiquement pour ce projet. Selon les technologies que vous
 utiliserez, vous pouvez reformuler certaines règles, à condition que le contenu et la substance
 de la règle restent inchangés. Il ne s’agit pas de modifier les règles pour les adapter au Marketing,
 mais bien de proposer une solution technique respectant la logique de la Compliance.
 Structure du corpus
 Le corpus contient des liens vers différents documents concernés par chaque règle. Trois types de
 documents devront être pris en compte :
 — la liste des disclaimers (mentions légales à ajouter selon les cas);
 — le prospectus du produit;
 — et le document Registration of Funds, un fichier Excel indiquant les pays dans lesquels un
 produit est autorisé à être commercialisé.
 1
À propos des disclaimers
 1. Les disclaimers sont des notes de bas de page destinées à ajouter une précision sur une
 information présente sur la slide ou, plus généralement, relative au document.
 2. Certains disclaimers diffèrent selon que le client est professionnel ou non professionnel.
 3. Voici une liste d’exemples de disclaimers :
 a. OBAM Presentation : disclaimer visant à introduire Oddo BHF Asset Management —
 il doit être présent sur toutes les présentations.
 b. Commercial Documentation : même idée, selon la structure du document.
 c. Commercial documentation (Luxembourg funds– RAIF).
 d. Opinion : disclaimer visant à dédouaner les opinions exprimées dans le document.
 e. Performance : mention précisant que les performances passées ne préjugent pas des per
formances futures.
 f. ESG Risk : en cas de mention de critères ESG.
 g. Issuers mentioned : concerne toute mention d’une entreprise ou la présence de son logo.
 h. Back tested performance : idée similaire à Performance.
 i. Simulations of future performance : si des prévisions sont proposées dans le document.
 j. YtM/YtW : si l’un de ces deux termes apparaît.
 k. Additional Information : mention explicite.
 l. Money Market Fund : lorsque ce type de fond est mentionné.
 m. SFDR : lorsqu’un des articles de la réglementation est cité.
 n. SRI : lorsque les risques sont mentionnés (dans un document marketing ou un script de
 vidéo).
 o. New Offer : doit être présent si le document fait référence à une nouvelle stratégie.
 Le prospectus du produit
 Le prospectus regroupe l’ensemble des caractéristiques d’un fond ainsi que les éléments de contenu
 que le document marketing ne peut pas contredire. Voir les règles pour en savoir plus.
 Registration of funds
 Dans les trois exemples fournis, la règle s’applique une fois (exemple 2). Cependant, lorsqu’il s’agit
 d’un nouveau produit (une des métadonnées fournies), celui-ci ne figure pas encore dans ce document
 —votre agent ne pourra donc pas traiter ce cas. En d’autres termes, ce document ne doit être pris en
 compte que si le produit n’est pas nouveau, afin de vérifier les pays de commercialisation autorisés.
 Jeu de données fourni
 Le jeu de données accompagnant ce document répond à deux objectifs :
 1. Business : Comprendre le type de document à traiter et la manière dont la Compliance apporte
 son expertise pour le rendre conforme.
 2. Technique : Mesurer la qualité de vos résultats et leur alignement avec le travail réel effectué
 par la Compliance Marketing. Vous avez toute liberté dans la construction de votre solution,
 mais il est vivement recommandé :
 — d’utiliser les documents fournis pour constituer un jeu de validation,
 — de définir des métriques pertinentes pour évaluer votre modèle,
 — et de structurer votre approche en briques logiques testables (tests unitaires).
 2
Notes importantes
 — Cejeudedonnées est évolutif : de nouveaux documents vous seront transmis au fil des semaines
 pour enrichir votre compréhension et renforcer la robustesse de votre solution.
 — Chaque exemple contient :
 — le document initial annoté par la Compliance (et parfois traduit),
 — le document attendu,
 — le prospectus associé au fond,
 — ainsi que des métadonnées connues à l’avance :
 — type de clients : professionnels ou retail?
 — entité juridique de la société de gestion : Oddo BHF Asset Management SAS / GmbH
 / Lux ?
 — la SICAV Oddo est-elle impliquée?
 — le document fait-il référence à une nouvelle stratégie? (utile pour les disclaimers)
 — ledocumentfait-il référence à un nouveau produit? (utile pour la Registration of Funds)
 — langue du document?
 — Il est fortement conseillé de lire l’ensemble des documents fournis avant de concevoir
 la solution technique, afin de bien comprendre le processus global et les points clés. Il n’est pas
 nécessaire de connaître toutes les règles par cœur : l’important est que votre solution applique
 les bonnes règles aux bonnes parties du document.

 Règles relatives aux présentations commerciales standards :
________________________________________
1 – Règles générales :
•	Si document retail : inclure les disclaimers retail (cf. Glossaire des disclaimers )
•	Si document professionnel : inclure les disclaimers professionnels (cf. Glossaire des disclaimers)
•	Les  études/ données chiffrées /graphiques etc., doivent faire l’objet d’un renvoi (note de bas de page)  précisant à minima la source et la date
•	Pour chaque fonds présenté : mention obligatoire du SRI avec le disclaimer associé sur la même slide (cf. Glossaire)
•	Pour les présentations retail : inclure un Glossaire des termes techniques en fin de présentation et s’assurer que ces termes figurent dans le document
•	Les avertissements/disclaimers sur les risques doivent :
o	être en gras
o	utiliser la même police et taille que le texte principal
o	être visibles (pas en note de bas de page)
•	Les opinions et hypothèses doivent être atténuées : Ex. : « selon notre opinion », « selon nos analyses », « le fonds a pour objectif de… »
•	La stratégie du fonds doit être présentée conformément à la documentation légale : seuils d’investissement par classe d’actifs, stratégie, allocation géographique, ticket minimum, etc.
•	Les pays de commercialisation indiqués doivent être conformes aux dernières données (fichier EXCEL : « registration abroad » disponible : I:\service\DOC LIB\GENERAL\Registration abroad of Funds) 
•	Les limites internes (fixées par le comité risque ou le contrôle des risques) ne doivent pas apparaître dans aucune présentation car non contractuel
•	Éviter les anglicismes dans les présentations retail, ou les définir (notes de bas de page ou glossaire avec renvoi)
•	Les documents commerciaux relatifs à des stratégies sont réservés aux clients professionnels uniquement → inclure le disclaimer professionnel
•	Pas de confusion entre la présentation d’une stratégie et celle d’un fonds dans un même document
•	Pour la Belgique : si présentation à destination de clients non professionnels belges, s’assurer de la validation préalable de la FSMA
•	Éviter de mentionner d’autres fonds (Oddo ou autres) dans une présentation standard d’un fonds sauf si c’est une présentation de gamme. 
•	Ne pas dire qu'un ETF est liquide
•	Si deux documents sont des versions du même texte mais dans des langues différentes, l'alignement entre le sens de chaque phrase et les données doit être exact et cohérent. Chaque phrase dans une langue doit transmettre précisément les mêmes informations, intentions et nuances que son équivalent dans l'autre langue. Aucun ajout, omission ou modification du sens n'est autorisé.
________________________________________
2 – Page de garde - Présentation Standard (~30 pages):
•	Doit indiquer :
o	Le nom du fonds
o	le mois et l’année
o	la mention « document promotionnel »
o	la cible : retail ou professionnel
•	Pour les fonds en pré-commercialisation : mentionner en rouge et gras sur la page de garde :
« VEUILLEZ NOTER QUE LE FONDS N'A PAS ENCORE ÉTÉ AGRÉÉ PAR L'AUTORITÉ DES MARCHÉS FINANCIERS (à adapter selon le régulateur) ET N’A PAS ÉTÉ AUTORISÉ À ÊTRE COMMERCIALISÉ EN FRANCE OU DANS D'AUTRES ÉTATS MEMBRES DE L'UNION EUROPÉENNE OU DANS TOUTE AUTRE JURIDICTION.
LES INVESTISSEURS DÉCLARENT ET RECONNAISSENT QU'AUCUNE OFFRE OU PLACEMENT OU SOLLICITATION DIRECTE OU INDIRECTE N'A ÉTÉ FAITE À L'INITIATIVE DE LA SOCIÉTÉ DE GESTION.
CETTE PRÉSENTATION VOUS EST SOUMISE SUR UNE BASE CONFIDENTIELLE ET UNIQUEMENT À DES FINS DE DISCUSSION. ELLE NE CONSTITUE PAS UNE OFFRE OU UNE INVITATION À SOUSCRIRE DES PARTS DU FONDS. LES INFORMATIONS QUI Y SONT PRÉSENTÉES NE DOIVENT PAS ÊTRE INVOQUÉES POUR SOUSCRIRE DES PARTS DU FONDS ET PEUVENT FAIRE L'OBJET DE MODIFICATIONS. »
•	Mention “do not disclose” si document professionnel
•	Pour les documents spécifiques à un client, indiquer le nom du client
________________________________________
3 – La Slide 2 (après la page de garde - Présentation Standard) contient a minima :
•	Le disclaimer standard (retail ou professionnel) → attention à adapter le nom du fonds et les clients éligibles
•	La mention exhaustive du profil de risque, conformément au prospectus
•	Les pays de commercialisation (registration abroad)
________________________________________
4 – Pages suivantes :

•	Ne jamais commencer une présentation par la performance : commencer à minima par la présentation du fonds
•	La Notation Morningstar doit être accompagnée (si elle existe) :
o	de la date de calcul
o	de la catégorie Morningstar de référence
•	Les objectifs de nombre de lignes en portefeuille doivent être mentionnés dans le prospectus. Si la présentation mentionne un nombre de lignes dans le portefeuille, cela doit être précisé dans le prospectus, sinon ne pas le mentionner.
•	En fin de présentation : inclure les caractéristiques détaillées du fonds
•	Vérifier la conformité des données avec la documentation légale (KID, Prospectus, Annexe SFDR), les données doivent être cohérentes
•	Indication du responsable de la validation de la présentation, cohérente avec le disclaimer général et la société de gestion
•	Lorsqu’on présente une équipe de gestion, ajouter en bas de page que “L’équipe est susceptible de changer”
________________________________________
4.1 – Mentions spécifiques relatives à l’ESG – Hors fonds professionnels :
Distinguer l’approche ESG du fonds (cf. Cartographie ESG, disponible au lien suivant I:\service\OAM\PROCEDURES ET POLITIQUES OBAM SAS\CARTOGRAPHIE ESG) :
•	Engageante
•	Réduite
•	Limitée au prospectus
Consignes selon l’approche :
•	Approche engageante (≥ 20 % d’exclusion et ≥ 90 % du portefeuille couvert) → pas de limite à la communication ESG
•	Approche réduite → communication limitée à moins de 10 % du volume de la présentation de la stratégie (mesurable en nombre de caractères si nécessaire)
•	Approche limitée au prospectus → pas de mention ESG sauf dans un document réservé à un investisseur institutionnel professionnel
•	Autres fonds → aucune mention ESG, sauf mention des exclusions du socle commun OBAM
________________________________________
4.2 – Mentions spécifiques des valeurs au sein des présentations :
À NE PAS FAIRE :
•	Pas de recommandation d’investissement directe ou indirecte
•	Ne pas indiquer si une valeur est sous-évaluée / surévaluée / correctement évaluée
•	Ne pas suggérer une stratégie d’investissement
•	Ne pas comparer des valeurs entre elles
•	Ne pas citer plusieurs fois une même valeur
•	Pas de projections futures pour une valeur
•	Pas d’opinion sur la valeur actuelle/future d’un instrument
•	Ne pas dire acheter, vendre, renforcer une valeur
•	Ne pas faire d’analyse spécifique sur une valeur
•	Pas d’opinion favorable/défavorable sur un émetteur ou secteur restreint
•	L’usage de formules telles que « selon nous », « à notre avis », même au conditionnel, peut constituer une recommandation d’investissement selon le contexte
À FAIRE :
•	Évoquer les tendances de marché
•	Références aux taux de change, taux d’intérêt, matières premières, indicateurs macroéconomiques (sans mention d’un instrument ou émetteur)
•	Évoquer des secteurs généraux (attention si le secteur est restreint)
•	Donner des informations factuelles (ex. : événements récents, annonces publiques)
•	Mentionner des valeurs détenues dans le portefeuille + performances passées avec les disclaimers adéquats
•	Donner un exemple illustratif d’un émetteur ou d’une valeur, sans projection ni estimation de prix
•	Lors d’une interview : les gérants doivent se limiter à des faits connus du public ; peuvent commenter les données historiques, mais pas d’opinion sur la valeur ou le prix actuels/futurs
________________________________________
4.3 – Mentions spécifiques relatives aux performances :
Un document commercial ou une communication externe ne peut pas débuter par les performances mais au minimum par la présentation du fonds.  Ainsi les performances ne peuvent jamais représenter l’élément central d’un document commercial ou d’une communication externe quel qu’il soit. Elles ne doivent pas apparaitre de manière disproportionnée par rapport aux autres éléments (police de caractère identique au texte central).
Lorsque la présentation est destinée aux retails seules les performances des parts retails (pour le listé : CR, DR, CN, DN, GC) peuvent être présentées.
•	Quelle est la durée minimum de présentation des performances ?

Les performances doivent être présentées sur une durée minimum de 10 ans pour les performances annualisées et 5 ans pour les autres.
Toutefois, lorsque le fonds ne peut afficher un historique de 10 ans, les performances sont alors nécessairement présentées depuis la création du fonds.  

•	Sous quelle forme présenter les performances ?

Pour tous les pays ou tout type de clientèle cible, les performances doivent être présentées nécessairement sous forme de performances annuelles glissantes, annualisées et/ou cumulées (dans l’ordre que l’on souhaite). Si le fonds a moins de 3 ans d’historique, les performances cumulées ne sont toutefois pas affichées (sauf le YtD et MtD).
Pour l’Allemagne (exclusivement) :
1/ les performances annuelles glissantes sont accompagnées des performances depuis la création du fonds jusqu’à la première année de performance glissante.
2/ la première année de présentation des performances glissantes incorpore les frais de souscription maximum. Il en est de même pour les frais de rachat maximum (acquis ou non acquis au fonds) prévus dans le prospectus à mentionner sur la dernière année.

•	Cas des performances year to date (YTD)
Les performances en YTD peuvent être mentionnées à la stricte condition de l’affichage des performances sur 10 ans, 5 ans ,3 ans, 1 an et/ou depuis la création.  Elles ne peuvent en aucun cas être présentées seules. 
•	Cas des performances de moins d’un an
▪ Les fonds avec un historique de performances de moins d’un an ne peuvent en aucun cas afficher de performances.
▪ Toutefois, l’affichage des valeurs liquidatives (VL de référence et dernière VL) au travers d’un graphe d’évolution est autorisé à l’exception de l’Allemagne (simple mention de la 1ère et de la dernière VL sous forme de tableau).
▪ Les performances à moins d’un mois ne peuvent en aucun cas être affichées (à l’exception du YTD). 
•	Présentation des performances en cas d’indicateur de référence ou de benchmark
Les performances sont obligatoirement et en permanence comparées à l’indicateur de référence du fonds s’il existe.
Dans le cas où un fonds détermine une cible (ex. objectif de surperformance en valeur absolue ou cible + X%) dans son objectif ou sa stratégie d’investissement, la performance du fonds doit être nécessairement comparée à cette cible. 
Les performances ne peuvent être en aucun cas comparées à un autre indicateur de référence qui ne serait pas mentionné dans le prospectus/DIC du fonds et cela même à titre d’information.
Lorsqu’un benchmark est supprimé, il est nécessaire de laisser figurer les performances du benchmark sur la période concernée avec indication de la date de suppression du dit benchmark.
Lorsqu’un benchmark est modifié, il est nécessaire de chainer les deux benchmarks avec indication de la date de modification du dit benchmark.
•	Présentation des performances d’un benchmark autre que le benchmark officiel 
Il est possible de présenter la performance d’’autres indices/benchmarks (indices actions, obligataires, matières premières...) à la condition de séparer strictement cette présentation de celle des performances du fonds avec son benchmark officiel (slides différents en annexe ou dans la partie marchés financiers si elle existe dans la présentation).
Cette présentation d’autres indices/benchmarks ne peut en aucun cas s’accompagner de la présentation de la performance du fonds.

•	Performances nettes ou brutes ?
Les performances sont obligatoirement présentées nettes de tout frais de gestion pour la clientèle retail y compris au travers de la distribution (fixes, variables, commission de mouvement) à préciser dans le document. 
S’il est présenté des performances brutes pour la clientèle professionnelle, il est obligatoirement précisé de manière visible l’effet des commissions ou toute autre charge venant diminuer cette performance (frais de gestion fixes et frais de gestion variables).
•	Création de nouvelles parts d’un fonds déjà existant
Lors de la création d’une nouvelle part d’un fonds déjà existant, il est possible de mentionner les performances d’une autre part de ce même fonds (avec un historique de performance de plus d’un an) en ajoutant obligatoirement une mention explicite que les frais de la nouvelle part sont ceux de la part xx et qu’il convient de consulter les documents légaux afin de connaitre exactement les frais de cette nouvelle part.

•	Divers
La période de référence et la source des données doivent être clairement indiquées dans le document.
La mention d’un track record d’un autre fonds ou d’une stratégie ou d’une équipe de gestion est impossible pour les fonds à destination de la clientèle retail.

 Modalités pour les stratégies (pour clients professionnels exclusivement)

•	Où indiquer les performances dans un document ?
Un document commercial quel qu’il soit ou une communication externe ne peut pas débuter par les performances mais au minimum par la présentation de la stratégie. Ainsi les performances ne peuvent jamais représenter l’élément central d’un document commercial ou d’une communication externe quel qu’il soit. Elles ne doivent pas apparaitre de manière disproportionnée par rapport aux autres éléments (police de caractère).

•	Quelle est la durée minimum de présentation des performances ?
Les performances doivent être présentées sur une durée minimum de 10 ans.  
Toutefois, lorsque la stratégie ne peut afficher un historique de 10 ans, les performances sont alors nécessairement présentées depuis la création de la stratégie.  . En cas de performances back testées, il n’existe pas de période minimum de 10ans.
Lorsque la stratégie a moins de 3 ans d'historique, les performances cumulées ne sont pas affichées seules.

•	Cas des performances year to date (YTD)
Les performances en year to date (YTD) peuvent être mentionnées à la stricte condition de l’affichage des performances sur 10 ans, 5 ans, 3 ans, 1 an et/ou depuis la création. Elles ne peuvent en aucun cas être présentées seules. 

•	Présentation des performances en cas d’indicateur de référence ou de benchmark
Les performances sont obligatoirement et en permanence comparées au benchmark de la stratégie. Toutefois, elle peut être aussi comparé et seulement à titre d’information (à mentionner de manière explicite) à un autre benchmark (celui-ci doit être cohérent avec les moteurs de performance de la stratégie, et stable dans le temps). 
•	Performances nettes ou brutes ?
Les performances des stratégies peuvent être présentée brutes de frais (hors frais de gestion fixes et variables, commission de mouvement) à préciser dans le document. S’il est présenté des performances brutes, cela doit être obligatoirement mis en évidence via un disclaimer spécifique.
•	Divers
La période de référence et la source des données doivent être clairement indiquées dans le document.

 Modalités particulières pour les fonds investis en titres cotés
▪ Lorsqu’il y a eu une modification d’indicateur de référence et/ou de l’orientation de gestion et/ou du profil rendement risque de l’OPC, un commentaire doit être inséré de manière visible permettant d’identifier la nature et la date du ou des changements. Ce qui implique de conserver nécessairement les performances passées. Cette disposition s’applique aussi bien aux fonds ouverts qu’aux fonds dédiés.
▪ Il est possible de présenter les performances à compter de la modification d’indicateur de référence et/ou de la modification de l’orientation de gestion et/ou de la modification du profil rendement risque agréé par l’AMF à la condition que cette nouvelle période soit strictement supérieure à 1 an.  Cette disposition ne s’applique pas aux fonds dédiés.
▪ Les performances des indicateurs de référence sont indiquées selon les termes du prospectus (dividendes inclus par exemple pour les fonds actions)
▪ Dans le cadre d’une fusion entre 2 OPC, il est possible de reprendre l’historique de l’OPC absorbé si et seulement si les conditions suivantes sont réunies 1/ l’OPC absorbant est strictement créé par la fusion avec l’absorbé, ce qui exclut toute autre situation, 2/ la stratégie d’investissement, l’objectif de gestion, l’équipe de gestion et la structure de coûts sont strictement identiques. Dans le cas contraire la reprise de l’historique de performances est impossible sauf si le régulateur du pays du fonds absorbant accepte de mentionner les performances du fonds absorbé dans le DIC du fonds absorbant. Le disclaimer suivant est affiché avec les performances de l’absorbant : « les performances présentées sont celles du Fonds « xxxxxxxx» (de droit xxxx - lancé le xxxx) qui a été absorbé par le fonds « xxxxxxxxx » en date du xxxxxxxx. « xxxxxxxx » poursuit exactement la même stratégie d'investissement et le même objectif de gestion que le fonds « xxxxxxxx».  L'équipe de gestion et la structure des coûts restent inchangées.

Présentation des rendements pour les fonds datés
S’agissant des documents commerciaux/communications externes à destination du retail, les fonds datés qui précisent dans leur prospectus qu’ils ont une gestion active ne peuvent afficher ni le YTM (yield to maturity), ni le YTW (yield to worst). 
En revanche les fonds datés qui précisent dans leur prospectus qu’ils ont une stratégie de buy and hold ou buy and maintain peuvent afficher le YTM (yield to maturity) et le YTW (yield to worst).
En ce qui concerne les fonds à destination des clients professionnels, il n’existe pas de restriction.

Caractéristiques particulières pour les fonds de Private equity
L’évolution de la performance sous forme de TRI net est uniquement communiquée pour des fonds de capital-investissement professionnels en cours de vie. 
Interdiction d’afficher la performance d’un fonds retail sous forme de TRI net avant l’échéance du fonds.
Interdiction d’affichage d’un track-record d’un fonds institutionnel à une clientèle retail.

Simulations de performances futures
En cas de simulation de performances futures, les données de ces dernières doivent remplir les conditions suivantes :
▪ L'information ne se fonde pas sur des simulations de performances passées ni ne s'y réfère ;
▪ Elle repose sur des hypothèses raisonnables fondées sur des éléments objectifs ;
▪ Lorsque l'information est fondée sur des performances brutes, l'effet des commissions, des redevances ou autres frais est précisé ;

Les règles de bonnes pratiques suivantes doivent être respectées dans l’élaboration de simulations de performances futures : 
▪ Les simulations de performances sont réalisées sur la base d’hypothèses de marché réalistes ;
▪ Les hypothèses de volatilité utilisées dans un graphique de simulation de performances futures sont cohérentes avec les actifs sous-jacents, l’allocation et la durée d’investissement simulés ;
▪ Une simulation tient compte de l’horizon de placement et est basée sur des hypothèses raisonnables de marché cohérentes avec cet horizon (taux d’intérêts, volatilité, inflation, etc.) fondées sur des éléments objectifs ;
Il convient de ne pas utiliser des hypothèses économiques à long terme de taux d’intérêt pour simuler à court terme des performances futures de placement en taux d’intérêts.

Simulations de performances passées

L’utilisation d’une simulation de performance pour la période durant laquelle aucune donnée n’était encore disponible n’est autorisée que dans le cas suivant et sous réserve d’être correcte, claire et non trompeuse: la performance d’une nouvelle catégorie de parts d’un OPCVM ou d’un compartiment d’investissement existant peut être simulée sur la base de la performance d’une autre catégorie d’e part, sous réserve que la proportion que ces deux catégories d’actions représentent dans les actifs de l’OPCVM ne diffère pas substantiellement.
Ainsi toute simulation sur une part déjà existante est interdite.
Le recalcul des performances tient alors obligatoirement compte de la différence sur frais fixes, frais variables, devises…

Disclaimers obligatoires
Dans tous les cas, l’affichage du disclaimer doit s’effectuer juste en dessous ou à côté des performances et en caractère tout à fait lisible.
•	En cas de présentation de performances réalisées (clients professionnels et non professionnels), il convient d’afficher de manière obligataire le disclaimer suivant : « les performances passées ne présagent pas des performances futures et ne sont pas constantes dans le temps». Cet affichage doit s’effectuer juste en dessous ou à côté des performances et en caractère tout à fait lisible.
•	En cas de présentation de performances back testées (clients professionnels et seulement en France) il convient nécessairement d’afficher de manière obligatoire le disclaimer suivant : « Les chiffres se référent à des simulations des performances passées.  Ces simulations sont le résultat d'estimations d’OBAM SAS à un moment donné, sur la base de paramètres sélectionnés par Oddo BHF Asset Management, de conditions de marché à ce moment donné et de données historiques qui ne préjugent en rien de résultats futurs. En conséquence, ces simulations n’ont qu’une valeur indicative et ne sauraient constituer en aucune manière une promesse de rendement. ». 
•	En cas de simulation de performances futures (clients professionnels et non professionnels), les résultats de la simulation de performances futures doivent s’accompagner de manière obligatoire du disclaimer ci-après : « la simulation présentée ne constitue pas une prévision de la performance future de vos investissements. Elle a seulement pour but d’illustrer les mécanismes de votre investissement sur la durée de placement. L’évolution de la valeur de votre investissement pourra s’écarter de ce qui est affiché, à la hausse comme à la baisse ».

•	Dans le cas d’affichage de plusieurs scénarios (du type favorable, défavorable et neutre), rajouter :
« Les gains et les pertes peuvent dépasser les montants affichés, respectivement, dans les scénarios les plus favorables et les plus défavorables. En poursuivant, vous reconnaissez avoir pris connaissance de cet avertissement, l’avoir compris et en accepter le contenu ».

•	En cas de simulation de performances passées, rajouter :
« Les performances affichées ne représentent pas les performances réelles de la part X sur une période donnée. Elles sont issues de simulations calculées par la société de gestion à partir des performances de la part Y du même fonds, retraitées des frais de gestion fixes, des frais de gestion variables, devises » …... (liste non exhaustive à adapter) 
5 – Page de fin de présentation :
•	Mention légale de la SGP (cf. Glossaire)

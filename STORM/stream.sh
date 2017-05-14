#!/bin/bash

HOME=/home/blaunet/Documents/Twitter_Collection/
STORM=$HOME/STORM
LOGS=$HOME/raw_log
LEPEN='MLP, MLP2017, @MLP_officiel, Marine2017, lepen2017, LePen, Le Pen, AuNomDuPeuple'
MACRON='Macron, enmarche, #EmmanuelMacron, Macron2017, @EmmanuelMacron'
HAMON='@benoithammon, Hamon, ProjetBH, Hamon2017, AvecHamon'
MELENCHON='@JLMelenchon, JLM, jlm2017.fr, FranceInsoumise, France Insoumise, JLM2017, Mélenchon, Melenchon, Melenchon2017'
FILLON='@Fillon2017_fr, FF2017, FillonPresident, Fillon, @FrancoisFillon, Fillon2017'
POUTOU='@PhilippePoutou, Poutou2017, Philippe Poutou, P. Poutou, Poutou'
ASSELINEAU='@UPR_Asselineau, Asselineau, @Fasselineau'
DUPONT='@dupontaignan, NDA2017, Dupont-Aignan, Dupont Aignan'
ARTHAUD='@n_arthaud, Arthaud, Arthaud2017'
CHEMINADE='@JCheminade, Cheminade2017, cheminade2017.fr, Cheminade'
LASSALLE='Jean Lassalle,Lassalle2017, jeanlassalle2017.fr'
KEYWORDS=$LEPEN,$MACRON,$HAMON,$MELENCHON,$FILLON,$POUTOU,$ASSELINEAU,$DUPONT,$ARTHAUD,$CHEMINADE,$LASSALLE,'Presidentielle, Presidentielle2017'
i=`ls -t $LOGS | head -1`
while true; do
 ((i+=1))
# bin/storm jar $STORM/examples/storm-starter/target/storm-starter-0.9.2-incubating-jar-with-dependencies.jar storm.starter.PrintSampleStream 3FiKFKyL9DcqN6xGdjE2SmBnz 2TYAUAOtjmlAiPX7hmrIfbIrMRgbHLVoEQEyrepZEi98sWTRhC 428481625-AG6rsLueWzTmCZpGbEzGyfgv6pl0zGeyyNs1gIIC OTZtQVQLGGHgR1U1DXtZgH4V500vEomLGTKbcl4EovWLz $KEYWORDS>$LOGS/$i.json &

 bin/storm jar $STORM/examples/storm-starter/target/storm-starter-0.9.2-incubating-jar-with-dependencies.jar storm.starter.PrintSampleStream 2xnvLlGEFUkbQ5gbR5AeGxzkz OaTOUbwTVishxMvBoCM1NdUU3FnW5rfAn8PAaLdy0JWIgmawbq 842801389436833794-H9FulNHK55NBe2I5ep8XKQ5LBZk7BXp 7nJFgjz1GdxMfiGOyt3hCQmy8bio6xtnmkiSyyMQeUBoQ $KEYWORDS>$LOGS/$i &

#  bin/storm jar $STORM/examples/storm-starter/target/storm-starter-0.9.2-incubating-jar-with-dependencies.jar storm.starter.PrintSampleStream fsjvPXITnOYJSS6GgmBuZSJrJ cCiDL0JrMA0j34upDXHwHFI2YkPiXFJWM8iqjOcI2AAWO4fLeV 2711607450-mTDSFZ5JKCtWSS9TWPcZWQyYwVKK9H9jqgw1AZD xrFby5t6tS87eR4Hr87xHrdwTHf4UtBjttRM3DMW4YShh>$LOGS/$i &


 sleep 960
 #sleep 10
 #PID=`ps aux | grep 'storm' | head -1 | cut -d " " -f 3`
 PID=`pgrep -f java -u blaunet`
 #PID=`pgrep -fl java | grep 'storm' | head -1 | cut -d " " -f 1`
 echo $PID
 kill  $PID
done


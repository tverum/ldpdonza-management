# Betalingen

In de betalingsmodule zit alle functionaliteiten voor het genereren en beheren van de betalingen.
Het bedrag dat gehanteerd wordt voor de betalingen, wordt bepaald door een aantal regels, dewelke hieronder beschreven zijn.

## Algemeen

Een betaling bestaat uit:

- **lid** Een lid (geïdentificeerd door een club_id)
- **origineel_bedrag** Het bedrag dat er betaald moet worden voor het lid in kwestie
- **afgelost_bedrag** Het reeds afgelost bedrag
- **seizoen** Het seizoen waarvoor het lid een betaling moet doen.
- **mededeling** De mededeling waarmee er gematcht moet worden
- **status** De status van de betaling
- **aflossingen** De aflossingen (dit zijn datums waarop er een aflossing heeft plaatsgevonden)

## Berekening

Bij het berekenen van het **origineel_bedrag** wordt er rekening gehouden met een aantal regels:

- Iedere ploeg valt onder een **lidgeldklasse**. Dit komt overeen met het aantal trainingen voor deze ploeg.
- Voor ieder lid wordt er voor het basisbedrag gekeken naar de ploeg waarin dit lid speelt (in het seizoen van de betaling).
- Als het lid in meerdere ploegen speelt, wordt de hoogste lidgeldklasse weerhouden.
- Als het lid oudere broers of zussen heeft die in het desbetreffende seizoen ook in een ploeg spelen, dan krijgt dit lid een korting van €50.

Als een lid voor een bepaald seizoen niet in een ploeg zit, dan wordt er ook geen betaling voor hem/haar/hen gegenereerd.

## Stappen

De volgende stappen vinden plaats in het betalingsproces:

1. De betalingen worden gegenereerd. Op dit moment wordt de betaling geregistreerd in het systeem. De betalingsvoorstellen worden echter nog niet uitgestuurd.
2. De betalingen worden uitgestuurd. In dit geval krijgen de ouders een betalingsvoorstel.
3. De betalingen worden betaald. Hierbij wordt de gestructureerde medeling meegegeven aan de betaling
4. Een uittreksel wordt gedownload van de bank.
5. Het uittreksel (CSV) wordt ingelezen in de applicatie. Hierbij worden die betalingen die de correcte gestructureerde mededeling hebben automatisch gematcht met de bijbehordende betaling in het systeem.
6. Eens de betaling volledig afgelost is, komt deze op "voltooid" te staan.
7. Een betalingsattest wordt uitgestuurd met een klik op de knop.

## Tests

De volgende tests zijn geschreven om bovenstaand gedrag te garanderen:

- Test dat een lid zonder team geen betaling heeft
- Test dat een lid in een jeugdteam de correcte betaling krijgt
- Test dat een lid in een seniorsteam (slechts in 1 team) geen betaling heeft
- Test dat een lid in meerdere (jeugd)teams het correcte (maximum)bedrag krijgt.
- Test dat een lid in een jeugdploeg en in een seniorsploeg het bedrag van de jeugdploeg krijgt.
- Test dat een lid met een ouder familielid de juiste korting toegewezen krijgt.
- Test dat een lid in een seniorsteam met een ouder familielid geen betaling toegewezen krijgt.

TODO:

- Voor coaches, helpende handen, etc. mogen er geen betalingen gegenereerd worden.
- Github action opzetten voor automatische testen.


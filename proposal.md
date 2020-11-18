# MUSA 509 Final Project Proposal
## memebers : Jiaxuan Lyu, Chi Zhang

<br>
<h2><b>Abstract:</b></h2>
<p>
Due to the current COVID pandemic, we aim to make an app that could help people to plan their daily trips. COVID-19 is caused by a new coronavirus (called SARS-CoV-2) and will generate symptoms such as fever, cough, trouble breathing and etc. (<a href="https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html">CDC, 2020</a>). The World Health Organization suggests people to avoid COVID by wearing masks and keeping social distance. More guidance could be found <a href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public">here</a> (WHO, 2020). Therefore, regulating trips before head helps people to choose more efficient transportation mode and to decrease contact with others. In this project, the study city is Philadelphia. The function of our app will mimic what google map did: when the users are searching for the routes from starting point to destinations, they will get an interactive map shows different route choices. Additionally, they could choose to travel by walking, cycling or by bus. Moreover, the surrounding number of positive COVID cases will be visualized to help them regulate their trips.  
</p>

<br>

<h2>Data</h2>

<h3>Covid Data</h3>
<b>Source</b>: Open Data Philly & Carto
    <ul>
        <li><b>by date:</b> https://www.opendataphilly.org/dataset/covid-cases/resource/7ae481eb-563a-46fc-a108-b3d335e1e171</li>
        <li><b>by zipcode:</b> https://www.opendataphilly.org/dataset/covid-cases/resource/a8761883-f0c1-4d20-8369-f5050af8b85a</li>
    </ul>

<b>How to host</b>: PostgreSQL on AWS RDS

We expect to visualize daily zipcode data for a given zipcode; But there are uncertainties about the data: if the data are not accurate, alternatively, we might do some bar charts.


<br>
<br>

<h3>Bike Data </h3>
<b>Source</b>: <a href="https://www.rideindego.com/about/data/">Indego</a>
    <ul>
        <li><b>Live station Geojson:</b>https://kiosks.bicycletransit.workers.dev/phl</li>
    </ul>

<b>How to host</b>: PostgreSQL on AWS RDS

<br>

<h3>Bus Data </h3>
<b>Source</b>: <a href="http://www3.septa.org/hackathon/">Septa</a>
    <ul>
        <li>Real Time: https://developers.google.com/transit/gtfs-realtime/ </li>
    </ul>

<b>How to host</b>: PostgreSQL on AWS RDS

<br>

<h3>Walk Data</h3>
<b>Source</b>: Mapbox API

<br>
<br>

<h2>Wireframes</h2>

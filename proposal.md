# MUSA 509 Final Project Proposal
## APP: Daily Routes
## memebers : Jiaxuan Lyu, Chi Zhang

<br>
<h2><b>Abstract:</b></h2>
<p>
Due to the current COVID pandemic, we aim to make an app that could help people to search for their daily trips. With a real-time COVID map shows where they are, there are also four listed choices which are divided into two groups. One group is for amenities, which are Indego bike stations and hospitals. Another group is for food, which includes farmers markets and Chinese takeout. 
The customers start at entering their address in Philadelphia, then they will get choices to select either bike stations, hospitals, farmers markets or Chinese takeout. After they decide their destinations, they will get a map shows where the choices are, and a table shows related information about their chosen destination. By clicking on whether they would like to drive or walk there, they will get detailed instructions on the route. One notice is that they will only have choice of walking if they want to go to near bike stations. If there are no ideal amenities or food choices, the closest five choices will be listed, and then they could know how to drive there.  
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
<b>Figma Links</b>:
    <ul>
        <li>Editale link: https://www.figma.com/file/pHK7OMNewEXZMoOqrEHVcR/Travel-Navigation?node-id=0%3A1 </li>
        <li>Interactive Prototype: https://www.figma.com/proto/pHK7OMNewEXZMoOqrEHVcR/Travel-Navigation?node-id=2%3A61&scaling=scale-down </li>
    </ul>
Our web application provides variety of destination choices. The wireframe takes bikestation as an example. 
<img src="https://github.com/MUSA-509/final-project-jiaxuan-chi/blob/main/Travel_Navigation_Wireframes_v2.png" />

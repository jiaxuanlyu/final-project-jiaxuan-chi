# MUSA 509 Final Project Proposal
## APP: Daily Routes
## memebers : Jiaxuan Lyu, Chi Zhang

<br>
<h2><b>Abstract:</b></h2>
<p>
Due to the current COVID pandemic, we aim to make an app that could help people to search for their daily trips. With a real-time COVID map shows where they are, there are also four listed choices which are divided into two groups. One group is for amenities, which are Indego bike stations and hospitals. Another group is for food, which includes farmers markets and Chinese takeout. <br>
The customers start at entering their address in Philadelphia, then they will get choices to select either bike stations, hospitals, farmers markets or Chinese takeout. After they decide their destinations, they will get a map shows where the choices are, and a table shows related information about their chosen destination. By clicking on whether they would like to drive or walk there, they will get detailed instructions on the route. One notice is that they will only have choice of walking if they want to go to near bike stations. If there are no ideal amenities or food choices, the closest five choices will be listed, and then they could know how to drive there.  
</p>

<br>

<h2>Data</h2>

<h3>Covid Data</h3>

<b>Source</b>: Open Data Philly & Carto

<b>Accumulated COVID cases by zipcode:</b> https://www.opendataphilly.org/dataset/covid-cases/resource/a8761883-f0c1-4d20-8369-f5050af8b85a

<b>How to host</b>: python API request

The accumulated COVID cases by Philly zipcode is requested in real-time by using python API request method. 


<br>
<br>


<h3>Bike Data </h3>

<b>Source</b>: <a href="https://www.rideindego.com/about/data/">Indego</a>

<b>Live station Geojson:</b>https://kiosks.bicycletransit.workers.dev/phl

<b>How to host</b>: PostgreSQL on AWS RDS


<br>
<br>


<h3>Hospital Data </h3>

<b>Source</b>: Open Data Philly

<b>Philadelphia Hospitals:</b>https://www.opendataphilly.org/dataset/philadelphia-hospitals

<b>How to host</b>: PostgreSQL on AWS RDS


<br>
<br>


<h3>Farmers Markets</h3>

<b>Source</b>: Open Data Philly

<b>Farmers Markets Locations:</b>https://www.opendataphilly.org/dataset/farmers-markets-locations

<b>How to host</b>: PostgreSQL on AWS RDS


<br>
<br>


<h3>Chinese Takeouts</h3>

<b>Souce</b>: Open Data Philly

<b>Healthy Chinese Takeout:</b>https://www.opendataphilly.org/dataset/healthy-chinese-takeout

<b>How to host</b>: PostgreSQL on AWS RDS



<h2>Wireframes</h2>

<b>Figma Links</b>:
    <ul>
        <li>Editale link: https://www.figma.com/file/pHK7OMNewEXZMoOqrEHVcR/Travel-Navigation?node-id=0%3A1 </li>
        <li>Interactive Prototype: https://www.figma.com/proto/pHK7OMNewEXZMoOqrEHVcR/Travel-Navigation?node-id=2%3A61&scaling=scale-down </li>
    </ul>
Our web application provides variety of destination choices. The wireframe takes bikestation as an example. 
<img src="https://github.com/MUSA-509/final-project-jiaxuan-chi/blob/main/Travel_Navigation_Wireframes_v2.png" />

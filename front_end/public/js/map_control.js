let map

async function draw_notice(notice) {
    //let notice = JSON.parse(notice_str)
    clear_map()
    let actors = []
    let den_ngbs = []
    let apd_ngbs = []
    let features = []
    old_position = []
    let mark

    
    if (notice.tp == 3){ // Trillareration proof
        
        let curr_coord = [ notice.curr_coords[1], notice.curr_coords[0]]
        mark = notice.curr_coords

        if (!sets_in_map.hasOwnProperty(notice.bus_line)) {

            actors.push({
                "type": "Point",
                "popup": `${notice.bus_line}`,
                "coordinates": curr_coord
            })

            
            let ngs = []
            let ngs_n =[]
            await inspect_query({ "select": "position", "position": notice.ng, "time": notice.ts }, (response) => {
                if (!response.success) {
                    console.log("Failed to inspect neighbors ",notice.bus_line)
                    return
                }

                
                for (let i = 0; i < notice.ng.length; i++) {
                    if (notice.ng_ap.includes(response.result[notice.ng[i]][0])){
                        ngs.push(response.result[notice.ng[i]])
                    }else{
                        ngs_n.push(response.result[notice.ng[i]])
                    }
                }
                

                for (let i = 0; i < ngs.length; i++) {
                    apd_ngbs.push({
                        "type": "Point",
                        "popup": ngs[i][0],
                        "coordinates": [ngs[i][2],ngs[i][1]]
                    })

                }
    
            
                for (let i = 0; i < ngs_n.length; i++) {
                    den_ngbs.push({
                        "type": "Point",
                        "popup": ngs_n[i][0],
                        "coordinates": [ngs_n[i][2],ngs_n[i][1]]
                    })

                }

                sets_in_map[notice.bus_line] = true
                console.log(points_in_map)

            })

            L.geoJSON(actors, {
                style: styleActor,
                onEachFeature: (feature, layer) => {layer.bindPopup(feature.popup)},
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                }
            }).addTo(map);
        
            L.geoJSON(den_ngbs, {
                style: styleDeny,
                onEachFeature: (feature, layer) => {layer.bindPopup(feature.popup)},
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                }
            }).addTo(map);
        
            L.geoJSON(apd_ngbs, {
                style: styleApprov,
                onEachFeature: (feature, layer) => {layer.bindPopup(feature.popup)},
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                }
            }).addTo(map);
        } 
    }
    else if (notice.tp == 4){ // Plausibility verification proof
        let curr_coord = [ notice.curr_coords[1], notice.curr_coords[0]]
        mark = notice.curr_coord

        if (!sets_in_map.hasOwnProperty(notice.bus_line)) {
            
            actors.push({
                "type": "Point",
                "popup": `${notice.bus_line}`,
                "coordinates": curr_coord
            })

            await inspect_query({ "select": "position", "position": notice.bus_line, "time": notice.last_prov_ts }, (response) => {
                if (!response.success) {
                    console.log("Failed to inspect neighbors ",notice.bus_line)
                    return
                }

                date = new Date(notice.last_prov_ts*1000)
                old_position.push({
                    "type": "Point",
                    "popup": `${notice.bus_line} <br> ${date.getHours() + ":" + ("0" + date.getMinutes()).slice(-2) + ", "+ date.toDateString()}`,
                    "coordinates": [response.result[2],response.result[1]]
                })

                
            })
            L.geoJSON(actors, {
                style: styleActor,
                onEachFeature: (feature, layer) => {layer.bindPopup(feature.popup)},
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                }
            }).addTo(map);

            L.geoJSON(old_position, {
                style: styleOldActor,
                onEachFeature: (feature, layer) => {layer.bindPopup(feature.popup)},
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng);
                }
            }).addTo(map);

            L.circle([response.result[2],response.result[1]], {radius: 10000}).addTo(map);



        }
        sets_in_map[notice.bus_line] = true
        console.log(points_in_map)




    }

    


    if (mark){
        map.flyTo(mark)
    }
}


function clear_map() {
    map.eachLayer(function (layer) {
        if (!layer._url) {
            map.removeLayer(layer);
        }
    });
    routes_in_map = {}
    points_in_map = {}
    sets_in_map = {}
}

// MAP GLOBAL VARIABLES
function init_map() {
    map = L.map('map').setView([-22.905, -43.205], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    let bus_id_elem = document.getElementById('fineModalBusId')
    bus_id_elem.onchange = function() {
        inspect_query({ "select": "trips", "trips": bus_id_elem.value }, (res) => {
            if (!res.success) {
                alert(`Error: ${res.result}`)
                return
            }

            let trip_id_elem = document.getElementById('fineModalTripId')
            let trips_html = ""
            for (let i = 1; i <= res.result; i++) {
                trips_html += `<option value=${bus_id_elem.value};${i}> ${bus_id_elem.value};${i} </option>`
            }
            
            trip_id_elem.innerHTML = trips_html
        })
    }
}



var myStyle = {
    "color": null,
    "fillColor": null,
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.6,
    "radious": 10
};

var styleActor = {
    "color": "#000000",
    "fillColor": "#000000",
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.8,
    "radious": 6
};

var styleOldActor = {
    "color": "#000000",
    "fillColor": "#000000",
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.4,
    "radious": 6
};

var styleApprov= {
    "color": "#000000",
    "fillColor": "#028A0F",
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.6,
    "radious": 4
};

var styleDeny= {
    "color": "#000000",
    "fillColor": "#900603",
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.6,
    "radious": 4
};

var routes_in_map = {} // { bus_line: boolean }
var points_in_map = {} // { "epoch_index;input_index": boolean }
var sets_in_map = {} // { bus_id: boolean }

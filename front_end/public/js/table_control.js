let url // next epoch URL
let curr_page = 1

function build_url() {
    url = "/?"

    if (filter_options.filterBusLine) {
        url += `filterBusLine=${filter_options.filterBusLine}`
    }
    if (filter_options.fineTypeSelector) {
        if (url.length != 2) {
            url += '&'
        }
        url += `fineTypeSelector=${filter_options.fineTypeSelector}`
    }
    if (url.length != 2) {
        url += '&'
    }    
}


function build_table(table_id, pagination_id) {
    let table_elem = document.getElementById(table_id+"Body")
    let pagination_elem = document.getElementById(pagination_id)


    if (!notices_table) {
        table_elem.innerHTML = '<tr><td colspan="3" class="text-center">No data to show</td></tr>'
        pagination_elem.innerHTML = ''
        return
    }

    if (!url) {
        build_url()
    }

    // building table body
    table_elem.innerHTML = ""
    for (let i = 0; i < notices_table[curr_page-1].length; i++) {
        let notice = notices_table[curr_page-1][i]
        let icon_html
        if (notice.tp == 1) {
            icon_html = '<img class="" data-bs-toggle="tooltip" title="Out of route" style="width:14;height:16;" src="assets/images/directions_off.png" alt="directions off icon">'
        } else {
            icon_html = '<img class="" data-bs-toggle="tooltip" title="Late" style="width:14;height:16;" src="assets/images/late.png" alt="directions off icon">'
        }


        let tr_html = ''
        + `<tr class="clickable-row" id="${notice.epoch_index};${notice.input_index}">`
        + `<td>${notice.bus_line}</td>`
        + `<td class="text-center">${notice.ts}</td>`
        + `<td class="text-end">${icon_html}</td>`
        + `<td class="text-end">${notice.value}</td>`
        + `</tr>`

        table_elem.insertAdjacentHTML("beforeend", tr_html)
        document.getElementById(`${notice.epoch_index};${notice.input_index}`).onclick = () => {draw_notice(notice)}
    }    
    
    
    // building table pagination
    let prev_disabled = "" // previous page button state
    let next_disabled = "" // next page button state
    let next_epoch
    let prev_epoch
    let pagination_html = ''
    let prev_btn_html
    let next_btn_html

    // page check
    if (curr_page == 1) {
        prev_disabled = "disabled"
    }
    if (curr_page == notices_table.length) {
        next_disabled = "disabled"
    }

    // epoch check
    if (req_epoch < curr_epoch) {
        next_epoch = req_epoch + 1
    }
    if (req_epoch > 0) {
        prev_epoch = req_epoch - 1
    }
    
    // previous button
    if (prev_epoch != undefined && curr_page == 1) {
        prev_btn_html = `<li class="page-item"><a class="page-link" href="${url}epoch=${prev_epoch}" title="Previous-Epoch" > prev epoch </a></li>`
    }
    else {
        prev_btn_html = `<li class="page-item ${prev_disabled}"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${curr_page-1})" title="Previous-Page" > prev </button></li>`
    }
    pagination_html += prev_btn_html


    if (notices_table.length <= 5) {
        for (var i = 1; i <= notices_table.length; i++) {
            if (i == curr_page) {
                pagination_html += `<li class="page-item disabled"><button class="page-link" title="Page-${i}" > ${i} </button></li>`
            }
            else {
                pagination_html += `<li class="page-item"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${i})" title="Page-${i}" > ${i} </button></li>`
            }   
        }                  
    }
    else {
        if (curr_page - 3 > 1) {
            pagination_html += `<li class="page-item"><button class="page-link" onclick="page_change(1)" title="Page-${1}" > "${1}" </button></li>`
            pagination_html += `<li class="page-item"><button class="page-link" title="" > "..." </button></li>`
            pagination_html += `<li class="page-item"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${curr_page-1})" title="Page-${curr_page-1}" > Page-${curr_page-1} </button></li>`
        }
        else {
            for (let i = 1; i < curr_page; i++) {
                pagination_html += `<li class="page-item"><button class="page-link" title="Page-${i}" > ${i} </button></li>`
            }
        }
        
        pagination_html += `<li class="page-item disabled"><button class="page-link" title="Page-${curr_page}" > ${curr_page} </button></li>`

        if (curr_page + 3 < notices_table.length) {
            pagination_html += `<li class="page-item"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${curr_page+1})" title="Page-${curr_page+1}" > Page-${curr_page+1} </button></li>`
            pagination_html += `<li class="page-item"><button class="page-link" title="" > "..." </button></li>`
            pagination_html += `<li class="page-item"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${notices_table.length})" title="Page-${notices_table.length}" > ${notices_table.length} </button></li>`
        }
        else {
            for (let i = page+1; i <= notices_table.length; i++) {
                pagination_html += `<li class="page-item"><button class="page-link" title="Page-${i}" > ${i} </button></li>`
            }
        }
    }

    // next button
    if (next_epoch != undefined && curr_page == notices_table.length) {
        next_btn_html = `<li class="page-item"><a class="page-link" href="${url}epoch=${next_epoch}" title="Next-Epoch" > next epoch </a></li>`
    }
    else {
        next_btn_html = `<li class="page-item ${next_disabled}"><button class="page-link" onclick="page_change('${table_id}','${pagination_id}',${curr_page+1})" title="Next-Page" > next </button></li>`
    }
    pagination_html += next_btn_html


    pagination_elem.innerHTML = pagination_html
}

function page_change(table_id, pagination_id, page) {
    curr_page = page
    build_table(table_id, pagination_id)
}
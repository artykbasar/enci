// frappe.show_progress_list_view = function(title, percentage, description) {
//     const main_layout = cur_page.page.querySelector('.container')
//     var progress_chart = document.createElement('div');
//     progress_chart.className = "progress-chart"
//     progress_chart.title = title
//     var progress = document.createElement('div')
//     progress.className = "progress"
//     var progress_bar = document.createElement('div')
//     progress_bar.className = "progress-bar progress-bar-success"
//     progress_bar.title = title
//     progress_bar.style = "width: " + percentage + "%"
//     var progress_message = document.createElement('p')
//     progress_message.className = "progress-message text-muted small"
//     progress_message.style = "padding-top: 5px;"
//     progress_message.textContent = description
//     progress.appendChild(progress_bar)
//     progress_chart.appendChild(progress)
//     progress_chart.appendChild(progress_message)
    
    
//     if (document.querySelector(".list-progress")) {
//         document.querySelector(".list-progress").innerHTML = progress_chart.outerHTML
//     } else {
//         var list_progress = document.createElement('div');
//         list_progress.className = "list-progress"
//         list_progress.style = "padding-left: 20px; padding-right: 20px; display: none;"
//         list_progress.innerHTML = progress_chart.outerHTML
//         main_layout.insertBefore(list_progress, main_layout.children[1])
//         $('.list-progress').show('fold')
//     }
//     if (percentage == 100){
//         let div = document.querySelector(".list-progress")
//         setTimeout(() => {
//             $(div).hide('fold', () => div.remove());
//         }, 2 * 1000);
//     }
// };
// console.log('test')
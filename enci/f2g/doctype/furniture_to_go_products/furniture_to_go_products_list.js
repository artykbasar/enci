frappe.listview_settings['Furniture To Go Products'] = {
	onload: function(listview) {
		const f2g_to_item = "enci.f2g.doctype.furniture_to_go_products.furniture_to_go_products.sync_f2g_to_item_list_enqueue";
		// const sync_to_f2g = "enci.f2g.doctype.furniture_to_go_products.furniture_to_go_products.sync_f2g_to_item_list_enqueue"


		listview.page.add_actions_menu_item(__("Sync To F2G, Items"), function() {
			listview.call_for_selected_items(f2g_to_item);
		});
		listview.page.add_button(__("Sync To F2G"), function() {
			frappe.call({
                method: 'enci.f2g.doctype.furniture_to_go_products.furniture_to_go_products.sync_all_f2g_products',
                args: {

                },
                // disable the button until the request is completed
                // btn: $('.primary-action'),
                // freeze the screen until the request is completed
                freeze: false,
                callback: (r) => {
					return true;
                    // on success
                },
                error: (r) => {
                    // on error
                }
            })
		});

		const main_layout = cur_page.page.querySelector('.container')
		frappe.realtime.on("f2g_products_sync", function(data) {

			// frappe.show_progress_list_view(data.title, data.percentage, data.description)
					
			var progress_chart = document.createElement('div');
			progress_chart.className = "progress-chart"
			progress_chart.title = data.title
			var progress = document.createElement('div')
			progress.className = "progress"
			var progress_bar = document.createElement('div')
			progress_bar.className = "progress-bar progress-bar-success"
			progress_bar.title = data.title
			progress_bar.style = "width: " + data.percentage + "%"
			var progress_message = document.createElement('p')
			progress_message.className = "progress-message text-muted small"
			progress_message.style = "padding-top: 5px;"
			progress_message.textContent = data.description
			progress.appendChild(progress_bar)
			progress_chart.appendChild(progress)
			progress_chart.appendChild(progress_message)
			
			
			if (document.querySelector(".list-progress")) {
				document.querySelector(".list-progress").innerHTML = progress_chart.outerHTML
			} else {
				var list_progress = document.createElement('div');
				list_progress.className = "list-progress"
				list_progress.style = "padding-left: 20px; padding-right: 20px; display: none;"
				list_progress.innerHTML = progress_chart.outerHTML
				main_layout.insertBefore(list_progress, main_layout.children[1])
				$('.list-progress').show('fold')
			}
			if (data.percentage == 100){
				let div = document.querySelector(".list-progress")
				setTimeout(() => {
					$(div).hide('fold', () => div.remove());
				}, 2 * 1000);
			}
		});
	},
    button: {
        show(doc) {
            return doc.stock_level;
        },
        get_label() {
            return 'Sync';
        },
        get_description(doc) {
            return __('Sync {0} with F2G and Item', [`${doc.name}`])
        },
        action(doc) {
            frappe.call({
                method: 'enci.f2g.doctype.furniture_to_go_products.furniture_to_go_products.sync_f2g_to_item_list_enqueue',
                args: {
                    names: [doc.name]
                },
                // disable the button until the request is completed
                // btn: $('.primary-action'),
                // freeze the screen until the request is completed
                freeze: false,
                callback: (r) => {
					return true;
                    // on success
                },
                error: (r) => {
                    // on error
                }
            })
            
        }
    }

};
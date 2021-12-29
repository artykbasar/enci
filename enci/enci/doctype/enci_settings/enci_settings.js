// Copyright (c) 2021, Artyk Basarov and contributors
// For license information, please see license.txt


frappe.ui.form.on('ENCI Settings', {
	onload: function(frm) {
		frappe.realtime.on("sql_import_progress", function(data) {
					
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
			progress_message.textContent = data.description
			progress.appendChild(progress_bar)
			progress_chart.appendChild(progress)
			progress_chart.appendChild(progress_message)
			cur_frm.get_field("load_presets").set_description(progress_chart)
			if (data.percentage == 100) {
				cur_frm.get_field("load_presets").set_description("SQL data successfully has been loaded to the Database")
			}

		});
	}

});




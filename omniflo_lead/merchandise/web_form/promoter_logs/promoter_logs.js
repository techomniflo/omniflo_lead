frappe.ready(function() {
	// bind events here
	getLocation()
	function getLocation() {
		if (navigator.geolocation) {
		 navigator.geolocation.getCurrentPosition(showPosition);
		}
	}

	function showPosition(position) {
		console.log(position.coords.longitude)
		console.log(position.coords.latitude)
		frappe.web_form.set_value([latitude], [position.coords.latitude]);
		frappe.web_form.set_value([longitude], [position.coords.longitude]);
	  }

	  frappe.web_form.after_load = () => {
		getLocation()
	}


})
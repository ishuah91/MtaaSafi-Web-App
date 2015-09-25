Polymer({ is: "admin-list",
	properties: {
		name: {
			type: String,
			notify: true,
			reflectToAttribute: true
		},
		sortField: {
			type: String,
			value: "name",
			reflectToAttribute: true
		},
		admins: {
			type: Array,
			notify: true
		}
	},

	viewCommunity: function(event, detail, sender) {
		var admin = event.model.admin;
		window.location.href = "/mtaasafi/community/" + admin.id + "/";
	},

	changeSort: function(event, detail, sender) {
		this.sortField = this.$.tabs.selected;
		this.$.adminsList.render();
	},

	orderBy: function(a, b) {
		if (this.sortField == "name")
			return this.sortByName(a, b);
		else
			return this.sortByCount(a, b);
	},
	sortByName: function(a, b) {
		if (a.name > b.name)
			return 1;
		if (a.name < b.name)
			return -1;
		return 0;
	},
	sortByCount: function(a, b) {
		if (a.report_set.length > b.report_set.length)
			return -1;
		if (a.report_set.length < b.report_set.length)
			return 1;
		return 0;
	},

	toUpperCase: function(value) {
		if (value) return value.charAt(0).toUpperCase() + value.slice(1);
	},
});
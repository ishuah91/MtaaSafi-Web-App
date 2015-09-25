DatumModel = Polymer({ is: "datum-model",
	properties: {
		id: {
			type: Number
		},
		site: {
			type: Object
		},
		date: {
			type: Object,
		},
		time: {
			type: String
		},
		groups: {
			type: Array,
			notify: true,
		}
	},

	factoryImpl: function(id, site, date) {
		this.id = id;
		this.site = site;
		this.date = new Date(date);
		SC.allData.set(this.id, this);
	},

	// setDate: function(jsonDate) {
	// 	var format = d3.time.format("%b %d %Y");
	// 	this.date = format(new Date(jsonDate));
	// }
});
Polymer({ is: "report-list",
	behaviors: [
		Polymer.NeonAnimatableBehavior
    ],
	properties: {
		name: {
			type: String
		},
		reports: {
			type: Array
		},
		selected: {
			type: Object,
			notify: true,
			observer: "selectionChanged"
		},
		sortField: {
			type: String,
			value: "timestamp",
			reflectToAttribute: true
		},
		superUser: {
			type: Boolean,
			value: false
		},

		animationConfig: {
			type: Object,
			value: function() {
				return {
					'entry': [{
						name: 'fade-in-animation',
						node: this.$.back
					}],
					'exit': [{
						name: 'fade-out-animation',
						node: this.$.back
					}, {
						name: 'hero-animation',
						id: 'hero',
						fromPage: this
					}]
				};
			}
		}
	},

	viewDetail: function(e) {
		this.$.selector.select(this.$.reports.itemForElement(e.target));
		this.$.page.selected = 1;
	},

	selectionChanged: function(newVal, oldVal) {
		if (newVal)
			this.$.page.selected = 1;
		else
			this.$.page.selected = 0;
	},

    _onClose: function() {
		this.$.page.selected = 0;
		this.selected = null;
    },

	// paginate: function(e) {
	// 	this.$.reports.model = { reports: e.detail.data };
	// },

	back: function(e) {
		window.location.href = "/mtaasafi/all/";
	},

	complete: function() {
		if (this.$.page.selected === 0)
			this.selected = null;
	},

	changeSort: function(event, detail, sender) {
		this.sortField = this.$.tabs.selected;
		this.$.reports.render();
	},

	orderBy: function(a, b) {
		if (this.sortField == "timestamp")
			return this.sortByTime(a, b);
		else
			return this.sortByVotes(a, b);
	},
	sortByTime: function(a, b) {
		if (a.timestamp > b.timestamp)
			return -1;
		if (a.timestamp < b.timestamp)
			return 1;
		return 0;
	},
	sortByVotes: function(a, b) {
		if (a.upvote_set.length > b.upvote_set.length)
			return -1;
		if (a.upvote_set.length < b.upvote_set.length)
			return 1;
		return 0;
	},

	getThumbUrl: function(id) {
		return "/mtaasafi/get_thumbnail/" + id + "/339x255";
	},

	d3Date: function(timestamp) {
		var format = d3.time.format('%b %e %Y, %I:%M %p');
		return format(new Date(timestamp));
	},

	toUpperCase: function(value) {
		if (value) return value.charAt(0).toUpperCase() + value.slice(1);
	},

	deleteReport: function(){
		if (this.superUser && confirm("Are you sure you want to delete this report?")){
			this.$.deleteReport.url = this.selected.resource_uri;
			this.$.deleteReport.generateRequest();
			window.location.reload();
		}
	}
});
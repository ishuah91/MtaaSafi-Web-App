Polymer({ is: "map-interface",
	properties: {
		sw: {
			type: Object,
			notify: true
		},
		ne: {
			type: Object,
			notify: true
		},
		bounds: {
			type: Object,
			observer: "boundsChanged"
		},
		center: {
			type: Number,
		},
		Lmap: {
			type: Object,
		},
		topojson: {
			type: Object,
			notify: true,
		},
		filtertopojson: {
				type: Array,
				notify: true
		},
		mapId: {
			type: Number,
			notify: true
		},
		svgArray: {
			type: Array,
			value:[]
		},
		gArray: {
			type: Array,
			value:[]
		}
	},

	created: function() { SC.map = this; },

	updateMap: function() {
		this.createBaseMap();
		this.createControls();
		this.intializeVizualizationLayer("main");
		
		if (this.topojson) {
			this.setData("main", null, this.topojson);
			this.resetVizLayer(-1);
		}
		SC.Lmap.invalidateSize(false);
	},

	setData: function(layer, index, collection) {
		var path = d3.geo.path().projection(this.projection).pointRadius(8);
		data = topojson.feature(collection, collection.objects.name);

		if(layer == 'main')
			layerg = this.maing;
		else if(layer == 'filter')
			layerg = this.gArray[index];

		var feature = layerg.selectAll("path.site")
				.data(data.features)
			.enter().append("path")
			.classed('site', true)
			.attr('id', function(d, i) { return 'shape-' + d.id })
			.style({
				'fill': "#626262",
				'stroke-width': '2px',
				'stroke': "white" })
			.on("click", function(d, i) {
				if (window.location.href.replace(/^(?:\/\/|[^\/]+)*\//, "") == "mtaasafi/all/" || window.location.href.replace(/^(?:\/\/|[^\/]+)*\//, "") == "all/")
					window.location.href = "/mtaasafi/community/" + d.id + "/";
				else {
					d3.selectAll("map-interface .site").classed("active", false);
					$("#right-pane detail-card").remove();

					d3.select(this).classed("active", true);
					this.parentNode.appendChild(this);
					var detail = new DetailCard(d.properties.name, d.properties.text, d.geometry);
					$("#right-pane").prepend(detail);
					detail.center();
				}
			})
			// .on('mouseover', function(d) {
			// 	if (SC.allSites.get(d.id))
			// 		return SC.allSites.get(d.id).set('hovering', 'direct');
			// })
			// .on('mouseout', function(d) {
			// 	if (SC.allSites.get(d.id))
			// 		return SC.allSites.get(d.id).set('hovering', false);
			// })
			.each(function(d, i) {
				if (d.properties.group_set)
					for (var g = 0; g < d.properties.group_set.length; g++) {
						groupStr = d.properties.group_set[g].substring(0, d.properties.group_set[g].length - 1);
						groupId = groupStr.substring(groupStr.lastIndexOf("/") + 1, groupStr.length)
						d3.select(this).classed("group-" + groupId, true);
						if(layer == 'filter')
							d3.selectAll("map-interface .site.group-" + groupId).classed("hidden", true);
					}
				if (d.geometry.type == 'LineString' || d.geometry.type == 'MultiLineString' ) {
					d3.select(this).style({
						'stroke-width': '4px',
						'fill': 'none',
						'fill-opacity': '0',
						'pointer-events': 'stroke'
						 });
				} else {
					d3.select(this).style({
						'stroke-width': '0px',
						'fill-opacity': '0.9',
						'pointer-events': 'fill'
					});
				}
			});
			// 	new DatumModel(d.id, d3.select(this), d.properties.date);
			// 	SC.Site.create(d.id, d.properties.name, this, d3.geo.centroid(d), d);
			// });
		if (!this.sw && !this.ne)
			SC.Lmap.fitBounds([[d3.geo.bounds(data)[0][1], d3.geo.bounds(data)[0][0]],[d3.geo.bounds(data)[1][1], d3.geo.bounds(data)[1][0]]]);
		feature.attr("d", path);
		this.Lmap.on("viewreset", function() { feature.attr("d", path); });
		this.fire("data-ready");
		$('#gif-spinner').fadeOut(400, function() { this.remove(); });
		$('#small-gif-spinner').show();
	},

	drawFilterFeatures: function(){
		console.log(this.filtertopojson);
		for (var i = 0; i <= this.filtertopojson.length - 1; i++) {
			this.intializeVizualizationLayer('filter');
			this.setData('filter', i,this.filtertopojson[i]);
			this.resetVizLayer(i); 
		};
		this.fire("filter-data-ready");
		$('#small-gif-spinner').fadeOut(400, function() { this.remove(); });
	},

	intializeVizualizationLayer: function(layer) {
		var svg = d3.select(this.Lmap.getPanes().overlayPane).append("svg").attr('class', "viz-layer");
		if(layer == 'main'){
			this.svg = svg;
	    	this.maing = svg.append("g").attr("class", "leaflet-zoom-hide");
			this.Lmap.on("viewreset", this.resetVizLayer);
		} else if (layer == 'filter') {
			svg.style({'pointer-events': 'none'});
			this.svgArray.push(svg);
			var gPath = svg.append("g").attr("class", "leaflet-zoom-hide");
			gPath.style({'pointer-events': 'none'});
	    	this.gArray.push(gPath);
		};
	},

	resetVizLayer: function() {
		var bounds = d3.geo.bounds(topojson.feature(SC.map.topojson, SC.map.topojson.objects.name));
		var bottomLeft = SC.map.projection(bounds[0]);
		var topRight = SC.map.projection(bounds[1]);
		var padding = 10;
		var xOffset = -bottomLeft[0] + padding;
		var yOffset = -topRight[1] + padding;

		SC.map.svg
			.attr("width", topRight[0] - bottomLeft[0] + padding*2)
			.attr("height", bottomLeft[1] - topRight[1] + padding*2)
			.style("margin-left", bottomLeft[0] - padding + "px")
			.style("margin-top", topRight[1] - padding + "px");
		SC.map.maing.attr("transform", "translate(" + xOffset + "," + yOffset + ")");

		for (var i = SC.map.svgArray.length - 1; i >= 0; i--) {
			var topo = SC.map.filtertopojson[i];
	        var bounds = d3.geo.bounds(topojson.feature(topo, topo.objects.name));
	        var bottomLeft = SC.map.projection(bounds[0]);
			var topRight = SC.map.projection(bounds[1]);
			xOffset = -bottomLeft[0] + padding;
			yOffset = -topRight[1] + padding;
			
			SC.map.svgArray[i]
				.attr("width", topRight[0] - bottomLeft[0] + padding*2)
				.attr("height", bottomLeft[1] - topRight[1] + padding*2)
				.style("margin-left", bottomLeft[0] - padding + "px")
				.style("margin-top", topRight[1] - padding + "px");

			SC.map.gArray[i].attr("transform", "translate(" + xOffset + "," + yOffset + ")");
		};
	},

	projection: function(x) {
		var point = SC.map.Lmap.latLngToLayerPoint(new L.LatLng(x[1], x[0]));
		return [point.x, point.y];
	},

	createBaseMap: function() {
		if (this.mapId == 134 || this.mapId == 136)
			var Lmap = L.map(this.$['map_canvas'], { zoomControl: false, minZoom: 9, maxZoom: 11 });
		else
			var Lmap = L.map(this.$['map_canvas'], { zoomControl: false, minZoom: 5, maxZoom: 11 });
		this.Lmap = Lmap;
		SC.Lmap = Lmap;
		if (this.sw && this.ne) {
			this.bounds = new L.latLngBounds(
				new L.LatLng(this.sw.coordinates[1], this.sw.coordinates[0]), 
				new L.LatLng(this.ne.coordinates[1], this.ne.coordinates[0])
			);
		} else 
			this.bounds = new L.latLngBounds(new L.LatLng(-90, -180), new L.LatLng(90, 180));
		var mapbox = L.mapbox.tileLayer('davkutalek.map-m44e15tr').addTo(SC.Lmap).bringToFront();
		this.baselayer = mapbox;
		var baseLayers = { "MapBox": mapbox };
		return baseLayers;
	},
	createControls: function() {
		// L.control.layers(baseLayers, null, {position: 'topright'}).addTo(map);
		this.Lmap.zoomControl = L.control.zoom({position: 'bottomright'}).addTo(this.Lmap);
		$(".leaflet-right").css({ 'margin-right': '5px' });
		$(".leaflet-top").css({ 'top': '35px' });
	},

	boundsChanged: function() {
		this.Lmap.fitBounds(this.bounds);
		this.zoom = this.Lmap.getZoom();
		this.center = this.Lmap.getCenter();
	},
});

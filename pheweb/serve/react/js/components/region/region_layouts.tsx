import { Layout, Panel, LayoutDataLayersEntity } from 'locuszoom';
import { Region, LzConf, layout_types } from './components';
import { defer } from 'q';

import { Layouts, Data, createCORSPromise, DataSources, TransformationFunctions, Dashboard, populate } from 'locuszoom';

'use strict';

// DEPENDENCIES: This js depends on custom_locuszoom.js and region_layouts.js which need to be included first in html files. We are moving to webpack to take care of the dependencies and this documentation is
// an interim reminder
export const region_layout: (region: Region) => Layout = (region: Region) => {
	return {

		width: 800,
		height: 400,
		"min_width": 800,
		"min_height": 400,
		responsive_resize: 'both',
		"resizable": "responsive",
		"min_region_scale": 2e4,
		"max_region_scale": 20e6,
		"panel_boundaries": true,
		mouse_guide: true,

		"dashboard": {
			"components": [{
				type: 'link',
				title: 'Go to Manhattan Plot',
				text:' Manhattan Plot',
				url: '/pheno/' + region.pheno.phenocode
			},{
				type: 'move',
				text: '<<',
				title: 'Shift view 1/4 to the left',
				direction: -0.75,
				group_position: "start",
			},{
				type: 'move',
				text: '<',
				title: 'Shift view 1/4 to the left',
				direction: -0.25,
				group_position: "middle",
			},{
				type: 'zoom_region',
				button_html: 'z+',
				title: 'zoom in 2x',
				step: -0.5,
				group_position: "middle",
			},{
				type: 'zoom_region',
				button_html: 'z-',
				title: 'zoom out 2x',
				step: 1,
				group_position: "middle",
			},{
				type: 'move',
				text: '>',
				title: 'Shift view 1/4 to the right',
				direction: 0.25,
				group_position: "middle",
			},{
				type: 'move',
				text: '>>',
				title: 'Shift view 3/4 to the right',
				direction: 0.75,
				group_position: "end",
			},{
				"type": "download",
				"position": "right",
			}]
		},
		"panels": []
		}
}

export const association_layout: (region: Region) => Layout = (region: Region) => {
	return {
		"id": "association",
		"title": { "text": region.browser, "x": 55, "y": 30 },
		"proportional_height": 0.2,
		"min_width": 400,
		"min_height": 150,
		"y_index": 0,
		"margin": {
			"top": 10,
			"right": 50,
			"bottom": 40,
			"left": 50
		},
		"inner_border": "rgb(210, 210, 210)",
		"dashboard": {
			"components": [{
				"type": "toggle_legend",
				"position": "right",
				"color": "green"
			}]
		},
		"axes": {
			"x": {
				"label_function": "chromosome",
				"label_offset": 32,
				"tick_format": "region",
				"extent": "state",
				"render": true,
				"label": "Chromosome {{chr}} (Mb)"
			},
			"y1": {
				"label": "-log10 p-value",
				"label_offset": 28,
				"render": true,
				"label_function": null
			}
		},
		"legend": {
			"orientation": "vertical",
			"origin": { "x": 55, "y": 40 },
			"hidden": true,
			"width": 91.66200256347656,
			"height": 138,
			"padding": 5,
			"label_size": 12
		},
		"interaction": {
			"drag_background_to_pan": true,
			"drag_x_ticks_to_scale": true,
			"drag_y1_ticks_to_scale": true,
			"drag_y2_ticks_to_scale": true,
			"scroll_to_zoom": true,
			"x_linked": true,
			"y1_linked": false,
			"y2_linked": false
		},
		"data_layers":
			[{
				"id": "significance",
				type: "orthogonal_line",
				orientation: "horizontal",
				offset: -Math.log10(5e-8),
			},
			Layouts.get("data_layer", "recomb_rate", { unnamespaced: false }),
			{
				"namespace": {
					"default": "association",
					"ld": "ld"
				},
				"id": "associationpvalues",
				"type": "scatter",
				"point_shape": {
					"scale_function": "categorical_bin",
					"field": "association:most_severe",
					"parameters": {
						"categories": ["frameshift variant",
							"inframe deletion",
							"inframe insertion",
							"splice acceptor variant",
							"splice donor variant",
							"start lost",
							"stop gained",
							"stop lost",
							"TFBS ablation",
							"missense variant"],
						"values": ["triangle-up",
							"triangle-down",
							"triangle-down",
							"triangle-up",
							"triangle-up",
							"triangle-down",
							"triangle-down",
							"triangle-down",
							"triangle-down",
							"square"],
						"null_value": "circle"
					}
				},
				/*
			  "point_size": {
			  "scale_function": "if",
			  "field": "ld:isrefvar",
			  "parameters": {
			  "field_value": 1,
			  "then": 80,
			  "else": 40
			  }
			  },*/
				"point_size": {
					"scale_function": "categorical_bin",
					"field": "association:most_severe",
					"parameters": {
						"categories": ["frameshift variant",
							"inframe deletion",
							"inframe insertion",
							"splice acceptor variant",
							"splice donor variant",
							"start lost",
							"stop gained",
							"stop lost",
							"TFBS ablation",
							"missense variant"],
						"values": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80],
						"null_value": 40
					}
				},
				"color": [{
					"scale_function": "if",
					"field": "ld:isrefvar",
					"parameters": {
						"field_value": 1,
						"then": "#9632b8"
					}
				}, {
					"scale_function": "numerical_bin",
					"field": "ld:state",
					"parameters": {
						"breaks": [0, 0.05, 0.2, 0.4, 0.6, 0.8, 0.9],
						"values": ["#555555", "#357ebd", "#46b8da", "#5cb85c", "#f3ca54", "#eea236", "#d43f3a"]
					}
				}, "#B8B8B8"],
				fill_opacity: 0.7,
				"legend": [{
					"shape": "triangle-up",
					"color": "#B8B8B8",
					"size": 80,
					"label": "frameshift, splice acceptor, splice donor",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "square",
					"color": "#B8B8B8",
					"size": 80,
					"label": "missense",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "triangle-down",
					"color": "#B8B8B8",
					"size": 80,
					"label": "inframe indel, start lost, stop lost, stop gained",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#B8B8B8",
					"size": 40,
					"label": "other",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#9632b8",
					"size": 40,
					"label": "LD Ref Var",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#d43f3a",
					"size": 40,
					"label": "1.0 > r² ≥ 0.9",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#eea236",
					"size": 40,
					"label": "0.9 > r² ≥ 0.8",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#f3ca54",
					"size": 40,
					"label": "0.8 > r² ≥ 0.6",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#5cb85c",
					"size": 40,
					"label": "0.6 > r² ≥ 0.4",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#46b8da",
					"size": 40,
					"label": "0.4 > r² ≥ 0.2",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#357ebd",
					"size": 40,
					"label": "0.2 > r² ≥ 0.05",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#555555",
					"size": 40,
					"label": "0.05 > r² ≥ 0.0",
					"class": "lz-data_layer-scatter"
				}, {
					"shape": "circle",
					"color": "#B8B8B8",
					"size": 40,
					"label": "no r² data",
					"class": "lz-data_layer-scatter"
				}],
				fields: region.lz_conf.assoc_fields,
				// ldrefvar can only be chosen if "pvalue|neglog10_or_100" is present.  I forget why.
				id_field: "association:id",
				behaviors: {
					onmouseover: [{ action: "set", status: "selected" }],
					onmouseout: [{ action: "unset", status: "selected" }]
				},
				tooltip: {
					closable: false,
					"show": {
						"or": ["highlighted", "selected"]
					},
					"hide": {
						"and": ["unhighlighted", "unselected"]
					},
					html: region.lz_conf.tooltip_html.replace('PHENO', region.pheno.phenostring || region.pheno.phenocode)
				},

				"x_axis": {
					"field": "association:position",
					"axis": 1
				},
				"y_axis": {
					"axis": 1,
					"field": "association:pvalue|neglog10_or_100",
					"floor": 0,
					"upper_buffer": 0.1,
					"min_extent": [0, 10]
				},
				"transition": false,
			}],
		"description": null,
		"origin": {
			"x": 0,
			"y": 0
		},
		"proportional_origin": {
			"x": 0,
			"y": 0
		},
		"background_click": "clear_selections"
	};
}

export const genes_layout: (region: Region) => Layout = (region: Region) => {
	return {
		"id": "genes",
		"proportional_height": 0.15,
		"min_width": 400,
		"y_index": 6,
		"min_height": 100,
		"margin": {
			"top": 0,
			"right": 50,
			"bottom": 0,
			"left": 50
		},
		"axes": {
			"x": { "render": false },
			"y1": { "render": false },
			"y2": { "render": false }
		},
		"interaction": {
			"drag_background_to_pan": true,
			"scroll_to_zoom": true,
			"x_linked": true,
			"drag_x_ticks_to_scale": false,
			"drag_y1_ticks_to_scale": false,
			"drag_y2_ticks_to_scale": false,
			"y1_linked": false,
			"y2_linked": false
		},
		"dashboard": {
			"components": [{
				"type": "resize_to_data",
				"position": "right",
				"color": "blue"
			}]
		},
		"data_layers": [{
			"namespace": { "gene": "gene" },
			"id": "genes",
			"type": "genes",
			"fields": ["gene:gene"],
			"id_field": "gene_id",
			"highlighted": {
				"onmouseover": "on",
				"onmouseout": "off"
			},
			"selected": {
				"onclick": "toggle_exclusive",
				"onshiftclick": "toggle"
			},
			"transition": false,
			behaviors: {
				onclick: [{ action: "toggle", status: "selected", exclusive: true }],
				onmouseover: [{ action: "set", status: "highlighted" }],
				onmouseout: [{ action: "unset", status: "highlighted" }]
			},
			"tooltip": {
				"closable": true,
				"show": { "or": ["highlighted", "selected"] },
				"hide": { "and": ["unhighlighted", "unselected"] },
				"html": "<h4><strong><i>{{gene_name}}</i></strong></h4><div>Gene ID: <strong>{{gene_id}}</strong></div><div>Transcript ID: <strong>{{transcript_id}}</strong></div><div style=\"clear: both;\"></div>"
			},
			"label_font_size": 12,
			"label_exon_spacing": 3,
			"exon_height": 8,
			"bounding_box_padding": 5,
			"track_vertical_spacing": 5,
			"hover_element": "bounding_box",
			"x_axis": {
				"axis": 1
			},
			"y_axis": {
				"axis": 1
			},

		}
		],
		"title": null,
		"description": null,
		"origin": {
			"x": 0,
			"y": 225
		},
		"proportional_origin": {
			"x": 0,
			"y": 0.5
		},
		"background_click": "clear_selections",
		"legend": null
	}
}

export const clinvar_layout: (region: Region) => Layout = (region: Region) => {
	return {
		"id": "clinvar",
		"title": { "text": "", "x": 55, "y": 35, "style": { "font-size": 6 } },
		"y_index": 4,
		"min_width": 400,
		"min_height": 25,
		"proportional_height": 0.05,
		"margin": {
			"top": 0,
			"right": 50,
			"bottom": 0,
			"left": 50
		},
		"axes": {
			"x": {
				"label_function": "chromosome",
				"label_offset": 32,
				"tick_format": "region",
				"extent": "state",
				"render": false,
				"label": "Chromosome {{chr}} (Mb)"
			},
			"y1": {
				"label": "Clinvar",
				"label_offset": 28,
				"render": true,
				"ticks": [],
				"label_function": null
			}
		},
		"legend": {
			"orientation": "vertical",
			"origin": {
				"x": 55,
				"y": 40
			},
			"hidden": true,
			"width": 91.66200256347656,
			"height": 138,
			"padding": 5,
			"label_size": 12
		},
		"interaction": {
			"drag_background_to_pan": true,
			"drag_x_ticks_to_scale": true,
			"drag_y1_ticks_to_scale": true,
			"drag_y2_ticks_to_scale": true,
			"scroll_to_zoom": true,
			"x_linked": true,
			"y1_linked": false,
			"y2_linked": false
		},
		"data_layers": [{
			"namespace": { "clinvar": "clinvar" },
			"id": "associationpvalues",
			// "id": "clinvar:var",
			"type": "scatter",
			"point_shape": "diamond",
			"point_size": {
				"scale_function": "if",
				"field": "ld:isrefvar",
				"parameters": {
					"field_value": 1,
					"then": 80,
					"else": 40
				}
			},

			"color": "#FF0000",
			fill_opacity: 0.7,

			fields: ["clinvar:id", "clinvar:trait", "clinvar:clinical_sig", "clinvar:varName", "clinvar:chr",
				"clinvar:ref", "clinvar:alt", "clinvar:start", "clinvar:stop", "clinvar:y"],
			id_field: "id",
			behaviors: {
				onmouseover: [{ action: "set", status: "selected" }],
				onmouseout: [{ action: "unset", status: "selected" }],
				onclick: [{ action: "link", href: "https://www.ncbi.nlm.nih.gov/clinvar/variation/{{id}}", target: "_blank" }],

			},
			tooltip: {
				closable: false,
				"show": {
					"or": ["highlighted", "selected"]
				},
				"hide": {
					"and": ["unhighlighted", "unselected"]
				},
				html: "<h4><strong><i>{{clinvar:trait}}</i></strong></h4><div>variant: <strong>{{varName}}</strong></div><div>Significance: <strong>{{clinical_sig}}</strong></div>"
			},

			"x_axis": {
				"field": "clinvar:start",
				"axis": 1
			},
			"y_axis": {
				"axis": 1,
				"field": "clinvar:y",
				"floor": 0,
				"upper_buffer": 0.1,
				"min_extent": [0, 10]
			},
			"transition": false,
		}],
		"description": null,
		"origin": {
			"x": 0,
			"y": 0
		},
		"proportional_origin": {
			"x": 0,
			"y": 0
		},
		"background_click": "clear_selections",
	}
}


export const gwas_cat_layout: (region: Region) => Layout = (region: Region) => {
	return {
		"id": "gwas_cat",
		"title": { "text": "GWAS catalog + UKBB", "x": 55, "y": 30 },
		"y_index": 5,
		"proportional_height": 0.2,
		"min_width": 400,
		"min_height": 150,
		"margin": {
			"top": 10,
			"right": 50,
			"bottom": 20,
			"left": 50
		},
		"inner_border": "rgb(210, 210, 210)",
		"dashboard": {
			"components": [{
				"type": "toggle_legend",
				"position": "right",
				"color": "green"
			}]
		},
		"axes": {
			"x": {
				"label_function": "chromosome",
				"label_offset": 32,
				"tick_format": "region",
				"extent": "state",
				"render": true,
				"label": "Chromosome {{chr}} (Mb)"
			},
			"y1": {
				"label": "-log10 p-value",
				"label_offset": 28,
				"render": true,
				"label_function": null
			}
		},
		"legend": {
			"orientation": "vertical",
			"origin": {
				"x": 55,
				"y": 40
			},
			"hidden": true,
			"width": 91.66200256347656,
			"height": 138,
			"padding": 5,
			"label_size": 12
		},
		"interaction": {
			"drag_background_to_pan": true,
			"drag_x_ticks_to_scale": true,
			"drag_y1_ticks_to_scale": true,
			"drag_y2_ticks_to_scale": true,
			"scroll_to_zoom": true,
			"x_linked": true,
			"y1_linked": false,
			"y2_linked": false
		},
		"data_layers": [{
			"namespace": { "gwas_cat": "gwas_cat" },
			"id": "associationpvalues",
			"type": "scatter",
			"point_shape": {
				"scale_function": "if",
				"field": "gwas_cat:study",
				"parameters": { "field_value": "UKBB", "then": "circle", "else": "diamond" }
			},
			"color": {
				"scale_function": "if",
				"field": "gwas_cat:study",
				"parameters": {
					"field_value": "UKBB",
					"then": "#9632b8",
					"else": "#d43f3a"
				}
			},
			fill_opacity: 0.7,
			"legend": [{
				"shape": "circle",
				"color": "#9632b8",
				"size": 40,
				"label": "UKBB",
				"class": "lz-data_layer-scatter"
			},
			{
				"shape": "diamond",
				"color": "#d43f3a",
				"size": 40,
				"label": "GWAS catalog",
				"class": "lz-data_layer-scatter"
			}],
			fields: ["gwas_cat:id",
				"gwas_cat:or_beta",
				"gwas_cat:pmid",
				"gwas_cat:variant",
				"gwas_cat:chrom",
				"gwas_cat:risk_allele",
				"gwas_cat:risk_frq",
				"gwas_cat:pos",
				"gwas_cat:ref",
				"gwas_cat:alt",
				"gwas_cat:trait",
				"gwas_cat:study",
				"gwas_cat:log_pvalue"
			],
			id_field: "gwas_cat:variant",
			behaviors: {
				onmouseover: [{ action: "set", status: "selected" }],
				onmouseout: [{ action: "unset", status: "selected" }],
				onclick: [{ action: "link", href: "https://www.ncbi.nlm.nih.gov/pubmed/{{gwas_cat:pmid}}", target: "_blank" }]
			},
			tooltip: {
				closable: false,
				"show": { "or": ["highlighted", "selected"] },
				"hide": { "and": ["unhighlighted", "unselected"] },
				html: 'Variant:<strong>{{gwas_cat:variant}}</strong><br>\n\nTrait:<strong>{{gwas_cat:trait}}</strong><br>\n\neffect size:<strong>{{gwas_cat:or_beta}}</strong><br>\n\nLog-pval:<strong>{{gwas_cat:log_pvalue}}</strong><br>\n\nRisk allele:<strong>{{gwas_cat:risk_allele}}</strong><br>\n\nRisk allele frq:<strong>{{gwas_cat:risk_frq}}</strong><br>\n\nStudy:<strong>{{gwas_cat:study}}</strong><br>'
			},
			"x_axis": { "field": "gwas_cat:pos", "axis": 1 },
			"y_axis": {
				"axis": 1,
				"field": "gwas_cat:log_pvalue",
				"floor": 0,
				"upper_buffer": 0.1,
				"min_extent": [0, 10]
			},
			"transition": false,
		}],
		"description": null,
		"origin": {
			"x": 0,
			"y": 0
		},
		"proportional_origin": {
			"x": 0,
			"y": 0
		},
		"background_click": "clear_selections",
	}
}

export const finemapping_layout: (region: Region) => Layout = (region: Region) => {
	return {
		"id": "finemapping",
		"title": { "text": "credible sets", "x": 55, "y": 30 },
		"proportional_height": 0.2,
		"min_width": 400,
		"min_height": 150,
		"y_index": 2,
		"margin": {
			"top": 10,
			"right": 50,
			"bottom": 40,
			"left": 50
		},
		"inner_border": "rgb(210, 210, 210)",
		"dashboard": {
			"components": [{
				"type": "toggle_legend",
				"position": "right",
				"color": "green"
			}]
		},
		"axes": {
			"x": {
				"label_function": "chromosome",
				"label_offset": 32,
				"tick_format": "region",
				"extent": "state",
				"render": true,
				"label": "Chromosome {{chr}} (Mb)"
			},
			"y1": {
				"label": "posterior inclusion probability",
				"label_offset": 28,
				"render": true,
				"label_function": null
			}
		},
		"legend": {
			"orientation": "vertical",
			"origin": {
				"x": 55,
				"y": 40
			},
			"hidden": true,
			"width": 91.66200256347656,
			"height": 138,
			"padding": 5,
			"label_size": 12
		},
		"interaction": {
			"drag_background_to_pan": true,
			"drag_x_ticks_to_scale": true,
			"drag_y1_ticks_to_scale": true,
			"drag_y2_ticks_to_scale": true,
			"scroll_to_zoom": true,
			"x_linked": true,
			"y1_linked": false,
			"y2_linked": false
		},
		"data_layers": [{
			"id": "significance",
			type: "orthogonal_line",
			orientation: "horizontal",
			offset: -Math.log10(5e-8)
		},
		{
			"namespace": { "finemapping": "finemapping" },
			"id": "associationpvalues",
			"type": "scatter",
			"point_shape": {
				"scale_function": "categorical_bin",
				"field": "finemapping:most_severe",
				"parameters": {
					"categories": ["frameshift variant", "inframe deletion", "inframe insertion", "splice acceptor variant", "splice donor variant", "start lost", "stop gained", "stop lost", "TFBS ablation", "missense variant"],
					"values": ["triangle-up", "triangle-down", "triangle-down", "triangle-up", "triangle-up", "triangle-down", "triangle-down", "triangle-down", "triangle-down", "square"],
					"null_value": "circle"
				}
			},
			"point_size": {
				"scale_function": "categorical_bin",
				"field": "finemapping:most_severe",
				"parameters": {
					"categories": ["frameshift variant", "inframe deletion", "inframe insertion", "splice acceptor variant", "splice donor variant", "start lost", "stop gained", "stop lost", "TFBS ablation", "missense variant"],
					"values": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80],
					"null_value": 40
				}
			},
			"color": [{
				"scale_function": "numerical_bin",
				"field": "finemapping:cs",
				"parameters": {
					"breaks": [0, 1.1, 2.1, 3.1, 4.1],
					"values": ["#66165d", "#d86b33", "#4eab48", "#357ebd", "#ff0000"],
					"null_value": "#ff0000"
				}
			}, "#B8B8B8"],
			fill_opacity: 0.7,
			"legend": [{
				"shape": "triangle-up",
				"color": "#B8B8B8",
				"size": 80,
				"label": "frameshift, splice acceptor, splice donor",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "square",
				"color": "#B8B8B8",
				"size": 80,
				"label": "missense",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "triangle-down",
				"color": "#B8B8B8",
				"size": 80,
				"label": "inframe indel, start lost, stop lost, stop gained",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#B8B8B8",
				"size": 40,
				"label": "other",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#66165d",
				"size": 40,
				"label": "credible set 1",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#d86b33",
				"size": 40,
				"label": "credible set 2",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#4eab48",
				"size": 40,
				"label": "credible set 3",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#357ebd",
				"size": 40,
				"label": "credible set 4",
				"class": "lz-data_layer-scatter"
			}, {
				"shape": "circle",
				"color": "#ff0000",
				"size": 40,
				"label": "credible set > 4",
				"class": "lz-data_layer-scatter"
			}],

			fields: ["association:pvalue", "association:beta", "association:sebeta", "association:rsid", "finemapping:id", "finemapping:chr", "finemapping:position", "finemapping:ref", "finemapping:alt", "finemapping:prob", "finemapping:cs", "finemapping:most_severe", "finemapping:AF", "finemapping:fin_enrichment", "finemapping:INFO"],
			id_field: "finemapping:id",
			behaviors: {
				onmouseover: [{ action: "set", status: "selected" }],
				onmouseout: [{ action: "unset", status: "selected" }],
				onclick: [{ action: "link", href: "/variant/{{finemapping:chr}}-{{finemapping:position}}-{{finemapping:ref}}-{{finemapping:alt}}" }],
			},
			tooltip: {
				closable: false,
				"show": {
					"or": ["highlighted", "selected"]
				},
				"hide": {
					"and": ["unhighlighted", "unselected"]
				},
				html: '<strong>{{finemapping:id}}</strong><br><strong>{{association:rsid}}</strong><br><strong>{{finemapping:most_severe}}</strong><table><tbody><tr><td>prob</td><td><strong>{{finemapping:prob}}</strong></td></tr><tr><td>p-value</td><td><strong>{{association:pvalue|scinotation}}</strong></td></tr><tr><td>beta</td><td><strong>{{association:beta}}</strong> ({{association:sebeta}})</td></tr><tr><td>AF</td><td><strong>{{finemapping:AF|percent}}</strong></td></tr><tr><td>FIN enrichment</td><td><strong>{{finemapping:fin_enrichment}}</strong></td></tr><tr><td>INFO</td><td><strong>{{finemapping:INFO}}</strong></td></tr></tbody></table>'
			},

			"x_axis": {
				"field": "finemapping:position",
				"axis": 1
			},
			"y_axis": {
				"axis": 1,
				"field": "finemapping:prob",
				"floor": 0,
				"upper_buffer": 0.1,
				"min_extent": [0, 1.1]
			},
			"transition": false,
		}],
		"description": null,
		"origin": {
			"x": 0,
			"y": 0
		},
		"proportional_origin": {
			"x": 0,
			"y": 0
		},
		"background_click": "clear_selections"
	}
}

const datalayer = (pip : string,beta : string,color : string) : LayoutDataLayersEntity => {

	const datalayer_id : string = `colocalization_${pip}`
	const field : string = `colocalization:${pip}`

	return {
    "id": datalayer_id,
	type: "scatter",
	point_shape : {
		scale_function : "categorical_bin",
		field : `colocalization:${beta}|sign`  ,
		parameters : {
			categories : [ "positive", "zero", "negative"] ,
			values : [ "triangle-up" , "circle" , "triangle-down" ],
			null_value : "square"
		}
	},
    fields: [
	"colocalization:causalvariantid",
	"colocalization:position",
	"colocalization:variant",
	"colocalization:pip1",
	"colocalization:pip2",
	"colocalization:beta1",
	"colocalization:beta2",
	"colocalization:rsid",
	"colocalization:varid",
	"colocalization:phenotype1",	
	"colocalization:phenotype1_description",
	"colocalization:phenotype2",	
	"colocalization:phenotype2_description"	
    ],
    orientation: "horizontal",
    offset: -Math.log10(5e-8),
    "namespace": { "colocalization": "colocalization" },
    id_field: "colocalization:causalvariantid",
    behaviors: {
	onclick: [{ action: "toggle", status: "selected", exclusive: true }],
	onmouseover: [{ action: "set", status: "highlighted" }],
	onmouseout: [{ action: "unset", status: "highlighted" }]
    },
    "tooltip": {
	"closable": true,
	"show": { "or": ["highlighted", "selected"] },
	"hide": { "and": ["unhighlighted", "unselected"] },
	"html": `<strong>{{colocalization:phenotype2}}</strong><br/>
	         {{colocalization:phenotype2_description|truncate}}<br/>
             <strong>{{colocalization:variant}}</strong><br/>
                 <table>
                   <tbody>
                     <tr>
                       <td>pip1</td><td><strong>{{colocalization:pip1}}</strong></td>
                     </tr>
                     <tr>
                       <td>pip2</td><td><strong>{{colocalization:pip2}}</strong></td>
                     </tr>
                     <tr>
                       <td>beta1</td><td><strong>{{colocalization:beta1}}</strong></td>
                     </tr>
                     <tr>
                       <td>beta2</td><td><strong>{{colocalization:beta2}}</strong></td>
                     </tr>
                   </tbody>
                 </table>`
    },
    "x_axis": { "field": "colocalization:position", "axis": 1 },
    "y_axis": { "axis": 1, "floor": 0, "upper_buffer": 0.0, "min_extent": [0, 1.1], "field": field },
	"color": [color],
	legend :  [ { shape: "circle", "color" : color, size: 40, "label" : pip , "class" : "lz-data_layer-scatter" } ]
}
}

export const colocalization_layout: (region: Region) => Layout = (region: Region) => {
	return { "id": "colocalization",
		 "title": { "text": "Credible Set : Colocalization", "x": 55, "y": 30 },
		 "proportional_height": 0.2,
		 "min_width": 400,
		 "min_height": 150,
		 "y_index": 3,
		 "margin": { "top": 10, "right": 50, "bottom": 40, "left": 50 },
		 "inner_border": "rgb(210, 210, 210)",
		 "dashboard": { "components": [ { "type": "toggle_legend",
						  "position": "right",
						  "color": "green" } ] },
		 "axes": { "x": { "label_function": "chromosome",
				  "label_offset": 32,
				  "tick_format": "region",
				  "extent": "state",
				  "render": true,
				  "label": "Chromosome {{chr}} (Mb)" },
			   "y1": { "label": "colocalization",
				   "label_offset": 28,
				   "render": true,
				   "label_function": null } },
		 "legend": { "orientation": "vertical",
			     "origin": { "x": 55, "y": 40 },
			     "hidden": true,
			     "width": 91.66200256347656,
			     "height": 138,
			     "padding": 5,
			     "label_size": 12 },
		 "interaction": { "drag_background_to_pan": true,
				  "drag_x_ticks_to_scale": true,
				  "drag_y1_ticks_to_scale": true,
				  "drag_y2_ticks_to_scale": true,
				  "scroll_to_zoom": true,
				  "x_linked": true,
				  "y1_linked": false,
				  "y2_linked": false },
	    "data_layers": [ datalayer("pip1","beta1", "#FF0000"),
						 datalayer("pip2","beta2", "#0000FF")
						]
	}
}

export const panel_layouts : Map<layout_types,Layout> = new Map([
	['association' , association_layout] ,
	['genes' , genes_layout ] ,
	['clinvar' , clinvar_layout ] , 
	['gwas_cat' , gwas_cat_layout ],
	['finemapping' , finemapping_layout ], 
	['colocalization' , colocalization_layout ] ]);

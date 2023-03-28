/** Declaration file generated by dts-gen */
declare module 'locuszoom' {

    export interface Margin {
	top: number;
	right: number;
	bottom: number;
	left: number;
    }

    export interface Origin { x: number; y: number; }

    export class Dashboard { constructor(parent: Plot| Panel);
	                     destroy(force: boolean): Dashboard;
	                     hide(): Dashboard;
	                     initialize(): Dashboard;
	                     position(): Dashboard;
	                     shouldPersist(): boolean;
	                     show(): Dashboard;
	                     update(): void; }

    export type DataLayer = {
	render () : void;
	data : object[];
	layout : Layout;
	constructor(layout: object, parent: Panel);
	addField(fieldName: string, nameSpace: string, transformations: string|string[]): string;
	applyAllElementStatus(): void;
	applyBehaviors(selection: any): void;
	applyCustomDataMethods(): DataLayer;
	applyDataMethods(): DataLayer;
	createTooltip(data: string|object): DataLayer;
	destroyAllTooltips(): DataLayer;
	destroyTooltip(element_or_id: string|object, temporary: boolean): DataLayer;
	draw(): DataLayer;
	executeBehaviors(directive: string, behaviors: { action : string , status : string }): DataLayer;
	exportData(format?: 'csv' | 'tsv' | 'json'): string;
	fadeAllElements(): DataLayer;
	fadeElement(id: string, exclusive?: boolean): DataLayer;
	fadeElementsByFilters(t: any, exclusive?: boolean): DataLayer;
	filter(filters: any[], return_type: string): any[];
	filterElements(t: any): any[];
	filterIndexes(t: any): any[];
	getAbsoluteDataHeight(): number;
	getAxisExtent(dimension: string): number[];
	getBaseId(): string;
	getElementAnnotation(t: any, e: any): any;
	getElementById(id: string): object|null;
	getElementId(element: string|object): string;
	getElementStatusNodeId(element : string| object): string| null;
	getPageOrigin(): {x: number, y: number};
	getTicks(dimension: string, config: object): object[];
	hideAllElements(): DataLayer;
	hideElement(id: string, exclusive?: boolean): DataLayer;
	hideElementsByFilters(filters: string[][], exclusive?: boolean): DataLayer;
	highlightAllElements(): DataLayer;
	highlightElement(id: string, exclusive?: boolean): DataLayer;
	highlightElementsByFilters(filters: string[][], exclusive?: boolean): DataLayer;
	initialize(): DataLayer;
	moveDown(): DataLayer;
	moveUp(): DataLayer;
	positionAllTooltips(): DataLayer;
	positionTooltip(id: string): DataLayer;
	reMap(): Promise<void>;
	resolveScalableParameter<X,Y>(layout: Array<any>|number|string|object,
				      element_data: X,
				      data_index: number): Y;
	selectAllElements(): DataLayer;
	selectElement(id: string, exclusive?: boolean): DataLayer;
	selectElementsByFilters(filters: string[][], exclusive?: boolean): DataLayer;
	setAllElementStatus(status: string, toogle: boolean): DataLayer;
	setElementAnnotation<T>(element: string|object, key: string, value : T): DataLayer;
	setElementStatus(status: string, element: string | object, active: boolean, exclusive: boolean): DataLayer;
	setElementStatusByFilters(status: string, toogle: boolean, filters: any[], exclusive: boolean): DataLayer;
	showOrHideTooltip(element: string | object, first_time: boolean): DataLayer;
	unfadeAllElements(): DataLayer;
	unfadeElement(id: string, exclusive?: boolean): DataLayer;
	unfadeElementsByFilters(filters: string[][], exclusive?: boolean): DataLayer;
	unhideAllElements(): DataLayer;
	unhideElement(id: string, exclusive?: boolean): DataLayer;
	unhideElementsByFilters(filters : string[][], exclusive?: boolean): DataLayer;
	unhighlightAllElements(): DataLayer;
	unhighlightElement(id: string, exclusive?: boolean): DataLayer;
	unhighlightElementsByFilters(filters: string[][], exclusive?: boolean): DataLayer;
	unselectAllElements(): DataLayer;
	unselectElement(id: string, exclusive?: boolean): DataLayer;
	unselectElementsByFilters(t: any, exclusive?: boolean): DataLayer;
	updateTooltip(d: string|object, id: string): DataLayer;

	static Statuses: {
	    verbs: 'highlight' | 'select' | 'fade' | 'hide';
	    adjectives: 'highlighted' | 'selected' | 'faded' | 'hidden';
	    menu_antiverbs: 'unhighlight' | 'deselect' | 'unfade' | 'show';
	};

    } | LayoutDataLayersEntity;

    export class DataSources {
	constructor();
	add(ns: string, x: Data.Source|Array<any>|null): DataSources;
	addSource(ns: string, x: string): DataSources;
	fromJSON(ns: string): DataSources;
	get(ns: string): Data.Source;
	getSource(ns: string): Data.Source;
	keys(): string[];
	remove(ns: string): DataSources;
	removeSource(ns: string): DataSources;
	set(ns: string, x: Data.Source): DataSources;
	toJSON(): string;
	sources: { [key: string]: Data.Source; }
    }


    export class Legend {
	constructor(parent : Panel);
	hide(): void;
	position(): void;
	render(): void;
	show(): void;

    }

    export class Panel {
	title?: LayoutTitle
	/** @member {LocusZoom.Plot|null} */
	parent : Plot | null;
	/** @member {LocusZoom.Plot|null} */
	parent_plot : Plot | null;
	/** @member {String} */
	id : string
	/** @member {Boolean} */
	initialized : boolean;
	/**
	 * The index of this panel in the parent plot's `layout.panels`
	 * @member {number}
	 * */
	layout_idx : number;
	/** @member {Object} */
	svg : object;
	/**
	 * A JSON-serializable object used to describe the composition of the Panel
	 * @member {Object}
	 */
	layout : Layout;
	/** @member {Object} */
	data_layers : { [key: string]: DataLayer } | DataLayer[];
	/** @member {String[]} */
	data_layer_ids_by_z_index : string[];
	/**
	 * Track data requests in progress
	 * @member {Promise[]}
	 *  @protected
	 */
	data_promises : Promise<object>[];
	/** @member {Number[]} */
	x_ticks : number[];
	/** @member {Number[]} */
	y1_ticks : number[];
	/** @member {Number[]} */
	y2_ticks : number[];
	/**
	 * A timeout ID as returned by setTimeout
	 * @protected
	 * @member {number}
	 */
	zoom_timeout : number | null;

	/** @returns {string} */
	getBaseId() : string;



	/**
	 * There are several events that a LocusZoom panel can "emit" when appropriate, and LocusZoom supports registering
	 *   "hooks" for these events which are essentially custom functions intended to fire at certain times.
	 *
	 * The following panel-level events are currently supported:
	 *   - `layout_changed` - context: panel - Any aspect of the panel's layout (including dimensions or state) has changed.
	 *   - `data_requested` - context: panel - A request for new data from any data source used in the panel has been made.
	 *   - `data_rendered` - context: panel - Data from a request has been received and rendered in the panel.
	 *   - `element_clicked` - context: panel - A data element in any of the panel's data layers has been clicked.
	 *   - `element_selection` - context: panel - Triggered when an element changes "selection" status, and identifies
	 *        whether the element is being selected or deselected.
	 *
	 * To register a hook for any of these events use `panel.on('event_name', function() {})`.
	 *
	 * There can be arbitrarily many functions registered to the same event. They will be executed in the order they
	 *   were registered. The this context bound to each event hook function is dependent on the type of event, as
	 *   denoted above. For example, when data_requested is emitted the context for this in the event hook will be the
	 *   panel itself, but when element_clicked is emitted the context for this in the event hook will be the element
	 *   that was clicked.
	 *
	 * @param {String} event The name of the event (as defined in `event_hooks`)
	 * @param {function} hook
	 * @returns {function} The registered event listener
	 */
	on(event : 'layout_changed' | 'data_requested' | 'data_rendered' | 'element_clicked' | 'element_selection', hook : (() => void)) : (() => void);
	/**
	 * Remove one or more previously defined event listeners
	 * @param {String} event The name of an event (as defined in `event_hooks`)
	 * @param {eventCallback} [hook] The callback to deregister
	 * @returns {LocusZoom.Panel}
	 */
	off(event : 'layout_changed' | 'data_requested' | 'data_rendered' | 'element_clicked' | 'element_selection', hook : (() => void)) : Panel ;


	constructor(layout : Layout, parent : Plot|null);
	addBasicLoader(addBasicLoader : boolean): Panel;
	addDataLayer(layout: Layout): any;

	/**
	 * Clear all selections on all data layers
	 * @returns {LocusZoom.Panel}
	 */
	clearSelections(): Panel;

	/**
	 * Iterate over data layers to generate panel axis extents
	 * @returns {Panel}
	 */
	generateExtents(): Panel;


	generateTicks(axis: 'x'|'y1'|'y2'): number[]|object[];

	/**
	 * Get an array of panel IDs that are axis-linked to this panel
	 * @param {('x'|'y1'|'y2')} axis
	 * @returns {Array}
	 */
	getLinkedPanelIds(axis: 'x'|'y1'|'y2'): string[];


	/**
	 * Prepare the first rendering of the panel. This includes drawing the individual data layers, but also creates shared
	 * elements such as axes,  title, and loader/curtain.
	 * @returns {Panel}
	 */
	initialize(): Panel;

	initializeLayout(): any;

	/**
	 * Move a panel up relative to others by y-index
	 * @returns {Panel}
	 */
	moveDown(): Panel;

	/**
	 * Move a panel down (y-axis) relative to others in the plot
	 * @returns {Panel}
	 */
	moveUp(): Panel;

	/**
	 * When the parent plot changes state, adjust the panel accordingly. For example, this may include fetching new data
	 *   from the API as the viewing region changes
	 * @returns {Promise}
	 */
	reMap(): Promise<void>;

	/**
	 * Remove a data layer by id
	 * @param {string} id
	 * @returns {Panel}
	 */
	removeDataLayer(id: string): Panel;

	/**
	 * Update rendering of this panel whenever an event triggers a redraw. Assumes that the panel has already been
	 *   prepared the first time via `initialize`
	 * @returns {LocusZoom.Panel}
	 */
	render(): Panel;

	/**
	 * Render ticks for a particular axis
	 * @param {('x'|'y1'|'y2')} axis The identifier of the axes
	 * @returns {LocusZoom.Panel}
	 */
	renderAxis(axis: 'x'|'y1'|'y2'): any;

	resortDataLayers(): void;

	/**
	 * Force the height of this panel to the largest absolute height of the data in
	 * all child data layers (if not null for any child data layers)
	 * @param {number|null} [target_height] A target height, which will be used in situations when the expected height can be
	 *   pre-calculated (eg when the layers are transitioning)
	 */
	scaleHeightToData(target_height?: number|null): void;



	/**
	 * Set/unset element statuses across all data layers
	 * @param {String} status
	 * @param {Boolean} toggle
	 */
	setAllElementStatus(stuats: string, toogle: boolean): void;


 	/**
	 * Set the dimensions for the panel. If passed with no arguments will calculate optimal size based on layout
	 *   directives and the available area within the plot. If passed discrete width (number) and height (number) will
	 *   attempt to resize the panel to them, but may be limited by minimum dimensions defined on the plot or panel.
	 *
	 * @public
	 * @param {number} [width]
	 * @param {number} [height]
	 * @returns {Panel}
	 */
	setDimensions(width: number, height: number): Panel;

	/**
	 * Methods to set/unset element statuses across all data layers
	 * @param {String} status
	 * @param {Boolean} toggle
	 * @param {Array} filters
	 * @param {Boolean} exclusive
	 */
	setElementStatusByFilters(status: string, toogle: boolean, filters: string[], exclusive: boolean): void;

	/**
	 * Set margins around this panel
	 * @public
	 * @param {number} top
	 * @param {number} right
	 * @param {number} bottom
	 * @param {number} left
	 * @returns {Panel}
	 */

	setMargin(top: number, right: number, bottom: number, left: number): Panel;

	/**
	 * Set panel origin on the plot, and re-render as appropriate
	 *
	 * @public
	 * @param {number} x
	 * @param {number} y
	 * @returns {LocusZoom.Panel}
	 */
	setOrigin(x: number, y: number): Panel;

	/**
	 * Set the title for the panel. If passed an object, will merge the object with the existing layout configuration, so
	 *   that all or only some of the title layout object's parameters can be customized. If passed null, false, or an empty
	 *   string, the title DOM element will be set to display: none.
	 *
	 * @param {string|object|null} title The title text, or an object with additional configuration
	 * @param {string} title.text Text to display. Since titles are rendered as SVG text, HTML and newlines will not be rendered.
	 * @param {number} title.x X-offset, in pixels, for the title's text anchor (default left) relative to the top-left corner of the panel.
	 * @param {number} title.y Y-offset, in pixels, for the title's text anchor (default left) relative to the top-left corner of the panel.
	 *                         NOTE: SVG y values go from the top down, so the SVG origin of (0,0) is in the top left corner.
	 * @param {object} title.style CSS styles object to be applied to the title's DOM element.
	 * @returns {Panel}
	 */
	setTitle(title : string|{ text : string , x : number , y : number , style : object }|null): Panel;

	fadeAllElements(): any;

	fadeElementsByFilters(t: any, e: any): any;

	hideAllElements(): any;

	hideElementsByFilters(t: any, e: any): any;

	highlightAllElements(): any;

	highlightElementsByFilters(t: any, e: any): any;

	selectAllElements(): any;

	selectElementsByFilters(status: string, e: any): any;

	unfadeAllElements(): any;

	unfadeElementsByFilters(t: any, e: any): any;

	unhideAllElements(): any;

	unhideElementsByFilters(t: any, e: any): any;

	unhighlightAllElements(): any;

	unhighlightElementsByFilters(t: any, e: any): any;

	unselectAllElements(): any;

	unselectElementsByFilters(t: any, e: any): any;

	static DefaultLayout: Layout;

	/**
	 * Get an object with the x and y coordinates of the panel's origin in terms of the entire page
	 * Necessary for positioning any HTML elements over the panel
	 * @returns {{x: Number, y: Number}}
	 */
	getPageOrigin() : { x : number , y : number};


    }

    export class Plot {
	panels : { [key: string]: Panel };
	constructor(id: string, datasource: DataSources, layout: Layout);
	addPanel(layout: Layout): Panel;
	applyState<T>(state_changes: any): Promise<T>;
	clearPanelData(panelId : string, mode : string): Plot;
	initialize(): Plot;
	initializeLayout(): Plot;
	positionPanels(): Plot;
	refresh<T>(): Promise<T>;
	removePanel(id: string): Plot;
	rescaleSVG(): Plot;
	setDimensions(width : number, height : number): Plot;
	startDrag(panel: Panel, method: string): Plot
	stopDrag(): Plot;
        subscribeToData(fields : string[], success_callback : (param : any) => void, opts : boolean): any;
        sumProportional(dimension: string): number;
        static DefaultLayout: Layout;

    }

    export const StandardLayout: Layout;

    export const ext: { };

    export const version: string;

    export function createCORSPromise<X>(method: string, url: string, body?: string | {}, headers? : object, timeout? : number): Promise<X>;

    export function generateCurtain(): object;

    export function generateLoader(): object;

    export function getToolTipData<E>(node: Element): E;

    export function getToolTipDataLayer(node: Element): DataLayer;

    export function getToolTipPanel(node: Element): Panel;

    export function getToolTipPlot(node: Element): Plot;

    export function parseFields(data : object, html: string): string;

    export function parsePositionQuery(query: string): {chr:string, start: number, end:number} | {chr:string, position:number};

    export function populate(selector: string, datasources: DataSources, parameter: object): Plot;

    export function populateAll(selector: string, datasources: DataSources, layout: object): Plot[];

    export function positionIntToString(position: number, exponent: number, suffix: boolean): string;

    export function positionStringToInt(s: string): number;

    export function prettyTicks(range: number[], clip_range: string, target_tick_count : number): number[];

    export function subclass(t: any, e: any, ...args: any[]): any;

    export namespace Dashboard {
	class Component {
            constructor(t: any, e: any);

            destroy(t: any): any;

            hide(): any;

            position(): any;

            shouldPersist(): any;

            show(): any;

            update(): void;

            static Button(parent: Component): void;

	}

	namespace Components {
            function add<X>(name: string, cons: ((_ : X) => Component)): void;

            function get(name: string, layout: Layout, parent: Dashboard): Component;

            function list(): any;

            function set(nam: string, component: Component): void;

	}

    }

    export namespace Data {
	class AssociationSource {
            constructor(t: any);

            getURL(t: any, e: any, a: any): any;

            normalizeResponse(t: any): any;

            preGetData(t: any, e: any, a: any, i: any): any;

            static SOURCE_NAME: string;

	}

	class ConnectorSource {
            constructor(t: any);

            combineChainBody(t: any, e: any): void;

            getRequest(t: any, a: any, e: any): any;

            parseInit(t: any): void;

            parseResponse(t: any, e: any, a: any, i: any, s: any): any;

            static SOURCE_NAME: string;

	}

	class GeneConstraintSource {
            constructor(t: any);

            combineChainBody(e: any, t: any, a: any, i: any, s: any): any;

            fetchRequest(t: any, e: any, a: any): any;

            getCacheKey(t: any, e: any, a: any): any;

            getURL(): any;

            normalizeResponse(t: any): any;

            static SOURCE_NAME: string;

	}

	class GeneSource {
            constructor(t: any);

            extractFields(t: any, e: any, a: any, i: any): any;

            getURL(t: any, e: any, a: any): any;

            normalizeResponse(t: any): any;

            static SOURCE_NAME: string;

	}

	class GwasCatalog {
            constructor(t: any);

            combineChainBody(t: any, e: any, a: any, i: any, s: any): any;

            extractFields(t: any, e: any, a: any, i: any): any;

            findMergeFields(t: any): any;

            getURL(t: any, e: any, a: any): any;

            static SOURCE_NAME: string;

	}

	class LDSource {
            constructor(t: any);

            combineChainBody(t: any, e: any, a: any, i: any, s: any): any;

            findMergeFields(t: any, ...args: any[]): any;

            findRequestedFields(t: any, e: any): any;

            getRefvar(t: any, e: any, a: any): any;

            getURL(t: any, e: any, a: any): any;

            normalizeResponse(t: any): any;

            preGetData(t: any, e: any): void;

            static SOURCE_NAME: string;

	}

	class LDSource2 {
            constructor(...args: any[]);

            fetchRequest(t: any, e: any, a: any): any;

            getURL(t: any, e: any, a: any): any;

            static SOURCE_NAME: string;

	}

	class PheWASSource {
            constructor(t: any);

            getURL(t: any, e: any, a: any): any;

            static SOURCE_NAME: string;

	}

	class RecombinationRateSource {
            constructor(t: any);

            getURL(t: any, e: any, a: any): any;

            static SOURCE_NAME: string;

	}

	class Parameter {

	}
	class Source {
            constructor();
	    params : ({ [key: string ]: string; } | { [key: string ]: any; } | Parameter)

            annotateData(records : Object[], chain : Object) : Object[]|Promise<Object>;

            combineChainBody(t: any, e: any, a: any, i: any, s: any): any;

            extractFields(data : Object[], fields : string[], outnames : string[], trans: ((v : any)=>any)[]) : object[];

            fetchRequest (state: Object, chain: any, fields: any): Promise<any>;

	    getCacheKey: (state: Object, chain: any, fields: any) => string | undefined;

	    getData: (state : Object, fields : string[], outnames : string[], trans: ((v : any)=>any)[] ) => any;

	    getRequest: (state: Object, chain: any, fields: any) => string | undefined;

	    getURL: (state: Object, chain: any, fields: any) => string | undefined;

            normalizeResponse(data : Object[]|Object) : any;

            parseArraysToObjects(t: any, e: any, a: any, i: any): any;

            parseData(t: any, e: any, a: any, i: any): any;

            parseInit(init : string | { url : string , params : string}) : void;

            parseObjectsToObjects(t: any, e: any, a: any, i: any): any;

            parseResponse(resp : string | object, chain: Object, fields : string[], outnames : string[], trans: ((v : any)=>any)[] ) : Promise<{header: any, discrete: any, body: object[]}>;

            prepareData(t: any): any;

            toJSON(): JSON;

            static extend(constructorFun: (init : any) => void, uniqueName: string, base?: (string| any )): any;

	}

	class StaticSource {
            constructor(t: any);

            getRequest(t: any, e: any, a: any): any;

            toJSON(): any;

            static SOURCE_NAME: string;

	}

	function Field(t: any): any;

	function Requester(l: any): any;

    }

    export namespace DataLayers {
	function add(t: any, e: any): void;

	function extend(t: any, e: any, a: any): any;

	function get(t: any, e: any, a: any): any;

	function list(): any;

	function set(t: any, e: any): void;

    }

    export namespace KnownDataSources {
	function add(t: any): void;

	function clear(): void;

	function create(t: any, ...args: any[]): any;

	function extend(t: any, e: any, a: any): any;

	function get(t: any): any;

	function getAll(): any;

	function list(): any;

	function push(t: any): void;

	function setAll(t: any): void;

    }

    export namespace Layouts {
	function add(t: any, e: any, a: any): any;

	function get(t: any, e: any, a: any): any;

	function list(t: any): any;

	function merge(t: any, e: any): any;

	function set(t: any, e: any, a: any): any;

    }

    export namespace ScaleFunctions {
	function add(t: any, e: any): void;

	function get(t: any, e: any, a: any, i: any): any;

	function list(): any;

	function set(t: any, e: any): void;

    }

    export namespace TransformationFunctions {
	function add(t: any, e: any): void;

	function get(t: any): any;

	function list(): any;

	function set<X,Y>(name: string, e: (x : X) => Y): void;

    }

    export interface Layout {
	height?: number;
	width?: number;
	responsive_resize?: string;
	id?: string;
	title?: LayoutTitle | null;
	proportional_height?: number;
	min_width: number;
	min_height: number;
	y_index?: number;
	margin?: Margin;
	inner_border?: string;
	dashboard?: { components?: (ComponentsEntity)[] | null; };
	axes? : LayoutAxes;
	legend?: LayoutLegend | null;
	interaction?: LayoutInteraction;
	data_layers?: (LayoutDataLayersEntity)[] | null;
	description?: string | null;
	origin?: Origin;
	proportional_origin?: Origin;
	background_click?: string;
	resizable?: string;
	min_region_scale?: number;
	max_region_scale?: number;
	panel_boundaries?: boolean;
	mouse_guide?: boolean;
	cliparea?: { height: number;
		     origin: Origin;
		     width: number; };
	panels?: LayoutPanel[];
    }

    export interface LayoutPanel {

    }

    export interface LayoutTitle {
	text: string;
	x: number;
	y: number;
	style?: any;
    }

    export interface ComponentsEntity {
	type: string;
	position?: string;
	color?: string;
	title?: string;
	text?: string;
	url?: string;
	direction?: number;
	group_position?: string;
	button_html?: string;
	step?: number;
	class?: string;
	style?: string;
    }

    export interface LayoutAxes {
	x: LayoutAxesLabel;
	y1: LayoutAxesLabel;
    }

    export interface LayoutAxesLabel {
	extent?: string;
	label?: string;
	label_function?: null | string;
	label_offset?: number;
	render?: boolean;
	ticks? : string[];
	tick_format?: string;
    }
    export interface LayoutLegend {
	orientation: string;
	origin: Origin;
	hidden: boolean;
	width: number;
	height: number;
	padding: number;
	label_size: number;
    }

    export interface LayoutInteraction {
	drag_background_to_pan: boolean;
	drag_x_ticks_to_scale: boolean;
	drag_y1_ticks_to_scale: boolean;
	drag_y2_ticks_to_scale: boolean;
	scroll_to_zoom: boolean;
	x_linked: boolean;
	y1_linked: boolean;
	y2_linked: boolean;
    }

    export interface LayoutDataLayersEntity {
	behaviors?: LayoutBehaviors | null;
	color?: (ValueMap<string> | string) | (ValueMap<string> | string)[] | null;
	fields?: (string)[] | null;
	fill_opacity?: number | null | ValueMap<number>;
	id: string;
	id_field?: string | null;
	legend?: (LayoutLegendEntity)[] | null;
	namespace?: {[key: string]: string } | null;
	offset?: number | null;
	orientation?: string | null;
	point_shape?: ValueMap<string> | string | null;
	point_size?: ValueMap<number> | number | null;
	tooltip?: LayoutTooltip | null;
	transition?: boolean | null;
	type: string;
	x_axis?: LayoutAxis | null;
	y_axis?: LayoutAxis | null;
    }

    export interface ValueMap<V> {
	scale_function: string;
	field: string;
	parameters:
	{ breaks?: number[],
	  values?: number | number[] | string | string[] | null,
	  categories?: (string | number)[] | null,
	  values?: V[] | null | V | number | number[] | string | string[],
	  null_value?: V
	} |
	    { field_value: string | number,
	      then?: V,
	      else?: V };
    }



    export interface LayoutNamespace {
	conditional?: string;
	association?: string;
	ld?: string;
    }

    export interface LayoutParameters {
	categories?: (string)[] | null;
	values?: number | number[] | string | string[] | null;
	null_value?: number | number[] | string | string[];
    }

    export interface LayoutPointSizeParameters {
	categories?: (string)[] | null;
	values?: number | number[] | string | string[] | null;
	null_value?: number | number[] | string | string[];
    }

    export interface LayoutLegendEntity {
	shape: string;
	color: string;
	size: number;
	label: string;
	class: string;
    }

    export interface LayoutBehaviors {
	onmouseover?: (LayoutOnmouseoverEntityOrOnmouseoutEntity)[] | null;
	onmouseout?: (LayoutOnmouseoverEntityOrOnmouseoutEntity)[] | null;
	onclick?: (LayoutOnclickEntity)[] | null;
    }

    export interface LayoutOnmouseoverEntityOrOnmouseoutEntity {
	action: string;
	status: string;
    }

    export interface LayoutOnclickEntity {
	action: string;
	href?: string;
	status?: string;
	exclusive?: boolean;
	target?: string;
    }

    export interface LayoutTooltip {
	closable: boolean;
	show: LayoutShow;
	hide: LayoutHide;
	html: string;
    }

    export interface LayoutShow { or?: string[] | null; }

    export interface LayoutHide { and?: string[] | null; }

    export interface LayoutAxis {
	field?: string;
	axis: number;
	floor?: number;
	lower_buffer?: number;
	upper_buffer?: number;
	min_extent?: number[] | null;
    }

}

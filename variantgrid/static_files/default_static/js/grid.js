function getGrid(nodeId, unique_code) {
	return $("#grid-" + nodeId, "#" + unique_code);
}

function export_grid(nodeId, unique_code, export_type) {
	let grid = getGrid(nodeId, unique_code);
	let gridParam = grid.jqGrid('getGridParam', 'postData');
	gridParam['rows'] = 0; // no pagination
	gridParam['export_type'] = export_type;

	let querystring = EncodeQueryData(gridParam);
	let url = Urls.node_grid_export() + "?" + querystring;
	window.location = url;
}

function load_variant_details(variant_id) {
    var variant_details_url = Urls.variant_details(variant_id);
    var aWin = getAnalysisWindow();
    if (aWin.ANALYSIS_SETTINGS) {
        if (aWin.ANALYSIS_SETTINGS.open_variant_details_in_new_window) {
            const VARIANT_URL = Urls.view_variant(variant_id);
            let newWin = aWin.open(VARIANT_URL, '_blank');
            newWin.focus();
            return;
        } else {
            let annotation_version_id = aWin.ANALYSIS_SETTINGS["annotation_version"];
            if (annotation_version_id) {
                variant_details_url = Urls.variant_details_annotation_version(variant_id, annotation_version_id);
            }
        }
    }
    let editorContainer = $("#node-editor-container");
    editorContainer.html('<div class="editor-loading"><img src="/static/images/spinner.gif" /> Loading variant details...</div>');
    editorContainer.load(variant_details_url);
}

function getAnalysisWindow() {
    var aWin = window;
    if (typeof _getAnalysisWindow !== "undefined") {
        try {
            // Not sure what's going on here (leaking between tabs?) but I very rarely get
            // Error: Uncaught SecurityError: Blocked a frame with origin "X" from accessing a cross-origin frame.
            aWin = _getAnalysisWindow();
        } catch(e) {
            if (typeof RAISED_GET_ANALYIS_WINDOW_JS_ERROR == "undefined") {
                RAISED_GET_ANALYIS_WINDOW_JS_ERROR = true;
                console.log(e);
                var exception_string = e.message + '\n' + e.stack;
                createJSEvent(exception_string, 'W', true); // log to server
            }
        }
    } 
    return aWin;
}


function get_igv_data() {
    var aWin = getAnalysisWindow();
    return aWin.ANALYSIS_SETTINGS["igv_data"];
}

function replaceFilePrefix(replaceDict, bamFiles) {
    var replacedBamFiles = [];
    if (replaceDict) {
        for (var i=0 ; i<bamFiles.length ; ++i) {
            var bamFile = bamFiles[i];
            if (bamFile) {
                for (var fromValue in replaceDict) {
                    var toValue = replaceDict[fromValue];
                    if (bamFile.startsWith(fromValue)) {
                        bamFile = bamFile.replace(fromValue, toValue);
                        break;
                    }
                }
                replacedBamFiles.push(bamFile);
            }
        }
    } else {
        replacedBamFiles = bamFiles;
    }
    return replacedBamFiles;
}


function create_igv_url(locus, inputBams) {
	var IGV_DATA = get_igv_data();
	var url = IGV_DATA['base_url'];
	var params = ["genome=" + IGV_DATA['genome']];
	if (locus) {
    	params.push("locus=" + locus);
    }
	var bamFiles = [];
	var manual_zygosity_cohort = IGV_DATA["manual_zygosity_cohort"];
	if (manual_zygosity_cohort && manual_zygosity_cohort.length) {
    	for (var i=0 ; i<manual_zygosity_cohort.length ; ++i) {
    		bamFiles.push(manual_zygosity_cohort[i]);
    	}
    } else {
        bamFiles = inputBams;
    }
    
	var op = 'goto';
	if (bamFiles.length > 0) {
        var replaceDict = IGV_DATA["replace_dict"];
        var replacedBamFiles = replaceFilePrefix(replaceDict, bamFiles);
        var joinedFiles = replacedBamFiles.join()
        if (joinedFiles) {
    		params.push("file=" + joinedFiles);
    		op = "load";
    	}
	}
	url += '/' + op + '?';
	url += params.join("&");
	return url;
}


seen_igv_error = false;

function open_igv_link(locus, getBamsFunc) {
    var url = create_igv_url(locus, getBamsFunc);

    $.ajax({
        url: url,
        error: function(jqXHR, textStatus, errorThrown) {
            if (!seen_igv_error) {
                console.log(jqXHR);
                console.log(textStatus);
                console.log(errorThrown);

                var IGV_DATA = get_igv_data();
                var base_url = IGV_DATA['base_url'];
                var igvIntegrationUrl = Urls.igv_integration();
    
                var message = "<p>Could not connect to IGV - is it running and accepting connections on " + base_url + "?";
                message += "<p>See also <a target='_blank' href='" + igvIntegrationUrl + "'>IGV Integration</a>";
                
                $("#error-dialog").html(message).dialog({
                    minWidth: 500,
                    buttons: [
                        {   text: "OK",
                            click: function() {
                                $(this).dialog("close");
                            },
                        },
                    ],                
                });
                seen_igv_error = true;
            }
        },
        suppressErrors: true,
    });
}


function noBamsHere() {
    return [];    
}


function getViewVariantUrl(variantLink) {
    var variantId = $(variantLink).parent(".variant_id-container").attr("variant_id");
    return Urls.view_variant(variantId);
}

function setFullscreenVariantLink() {
  var url = getViewVariantUrl(this);
  $(this).attr('href', url);
}

function restoreVariantLink() {
  var orig_href = $(this).attr('orig_href');
  $(this).attr('href', orig_href);
}


function createGridLink(title, url, contents, extraLinkClasses, extraIconClasses) {
    var linkCSS = ['grid-link'];
    if (extraLinkClasses) {
        linkCSS = linkCSS.concat(extraLinkClasses);
    }
    var iconCSS = ['grid-link-icon', 'user-tag-colored'];
    if (extraIconClasses) {
        iconCSS = iconCSS.concat(extraIconClasses);
    }

    var gridBox = "<div class='" + iconCSS.join(' ') + "'>" + contents + "</div>";
    var link = $("<a/>").attr({"class" : linkCSS.join(' '),
                               "title" : title,
                               "orig_href" : url,
                               "href" : url});
    link.append(gridBox);
    return link.prop("outerHTML");
}

function createIgvUrl(locus, getBamsFuncString) {
    var aWin = getAnalysisWindow();
    if (aWin.ANALYSIS_SETTINGS && aWin.ANALYSIS_SETTINGS['show_igv_links']) {
        if (!getBamsFuncString) {
            getBamsFuncString = 'noBamsHere';
        }
        return 'javascript:open_igv_link("' + locus + '", ' + getBamsFuncString + '())';
    }
    return null;
}

function create_igv_link(locus, getBamsFuncString) {
    let igvUrl = createIgvUrl(locus, getBamsFuncString);
    if (igvUrl) {
        return createGridLink("Open " + locus + " in IGV", igvUrl, '', [], ['igv-link']);
    }
    return '';
}

function showGridCell(gridColumn) {
    var selector = $("td[aria-describedby*='" + gridColumn + "']");
    if (selector.length) {
        selector[0].scrollIntoView();
    }
}

function isNodeVisible(options) {
    // Default to True so that any cached grid data won't be missing new field
    let nodeVisible = true;
    let analysisNode = options.colModel.analysisNode;
    if (analysisNode) {
        nodeVisible = analysisNode.visible;
    }
    return nodeVisible;
}


function detailsLink(variantId, options, rowData) {
    let nodeVisible = isNodeVisible(options);
    let kwargs = options.colModel.formatter_kwargs;
    if (kwargs) {
        nodeVisible = kwargs.node_visible;
    }

    let variantBoxes = [];
    if (nodeVisible) {
        let variant_selector = "<input type='checkbox' class='variant-select' variant_id=" + variantId + ">";
        variantBoxes.push(variant_selector);
    }

    let detailsUrl = "javascript:load_variant_details(" + variantId + ");";
    let detailsLink = createGridLink('View details', detailsUrl, '', ['variant-link'], ['view-details-link']);
    variantBoxes.push(detailsLink);

    // ClinVar
    let cvHighestPath = rowData["clinvar__highest_pathogenicity"];
    let cvClinSig = rowData["clinvar__clinical_significance"];

    let linkUrl = null;
    let extraLinkClasses = ['node-count-legend-C'];
    let extraIconClasses = [];
    let cvTitle = "ClinVar: ";
    if (cvHighestPath !== null) {
        cvTitle += cvClinSig;
        linkUrl = 'javascript:showGridCell("clinvar__clinical_significance")';
    } else {
        cvTitle += "not classified";
        extraIconClasses.push("no-entry");
        cvHighestPath = '';
    }
    let cvLink = createGridLink(cvTitle, linkUrl, cvHighestPath, extraLinkClasses, extraIconClasses);
    variantBoxes.push(cvLink);

    // Internally Classified
    let intMaxClass = rowData["max_internal_classification"];
    let intClassified = rowData["internally_classified"];

    linkUrl = null;
    let icTitle = "Internally Classified: ";
    extraLinkClasses = ['node-count-legend-G'];
    extraIconClasses = [];

    if (intMaxClass !== null) {
        icTitle += intClassified;
        linkUrl = 'javascript:showGridCell("max_internal_classification")';
    } else {
        icTitle += "not classified";
        extraIconClasses.push("no-entry");
        intMaxClass = '';
    }
    let icLink = createGridLink(icTitle, linkUrl, intMaxClass, extraLinkClasses, extraIconClasses);
    variantBoxes.push(icLink);

    let locus = rowData["locus__contig__name"] + ":" + rowData["locus__position"];
    let igvLink = create_igv_link(locus, 'getBams');
    variantBoxes.push(igvLink);
    return "<span class='variant_id-container' variant_id=" + variantId + ">" + variantBoxes.join('') + "</span>";
}

function clinvarLink(clinvar_variation_id) {
    let clinvar_string = '';
    if (clinvar_variation_id) {
        clinvar_string = "<a title='View ClinVar entry in new window' target='_blank' href='http://www.ncbi.nlm.nih.gov/clinvar/variation/" + clinvar_variation_id + "'>" + clinvar_variation_id + "</a>";
    }
    return clinvar_string;
}

function cosmicLink(cosmic_ids) {
    const COSMIC_PREFIX = "COSV";
    const COSMIC_LEGACY_PREFIX = "COSM";

    var cosmic_string = '';
    if (cosmic_ids) { 
        var cosmic_ids_list = cosmic_ids.split("&");
        var cosmic_links = [];
        for(var i=0 ; i<cosmic_ids_list.length ; ++i) {
            var cosmic_id = cosmic_ids_list[i];
            if (cosmic_id.startsWith(COSMIC_PREFIX)) {
                // #2637 - COSMIC switched to using COSV in 2019, I can't find a direct link but search works then you select transcript
                cosmic_id = "<a title='View COSMIC entry in new window' target='_blank' href=' https://cancer.sanger.ac.uk/cosmic/search?q=" + cosmic_id + "'>" + cosmic_id + "</a>";
            } else if (cosmic_id.startsWith(COSMIC_LEGACY_PREFIX)) {
                var cosmic_id_int = cosmic_id.replace("COSM", "");
                cosmic_id = "<a title='View COSMIC entry in new window' target='_blank' href='http://cancer.sanger.ac.uk/cosmic/mutation/overview?id=" + cosmic_id_int + "'>" + cosmic_id + "</a>";
            }
            cosmic_links.push(cosmic_id);
        }
        
        cosmic_string = cosmic_links.join();
    }
    return cosmic_string;
}


function omimLink(omim_id) {
    var omim_string = '';
    if (omim_id) {
        omim_string = "<a title='View OMIM entry in new window' target='_blank' href='https://www.omim.org/entry/" + omim_id + "'>" + omim_id + "</a>";
    }
    return omim_string;
}


function _geneSymbolLink(geneSymbolColumn, filterChildLink) {
    var columnString = '';
    if (geneSymbolColumn) {
        var geneSymbolList = geneSymbolColumn.split(",");
        var geneSymbolLinks = [];
        for(var i=0 ; i<geneSymbolList.length ; ++i) {
            let geneSymbol = geneSymbolList[i];
            let geneLinkString = '';
            if (filterChildLink) {
                let filterGeneLink = "javascript:createFilterChild(\"gene_symbol\", \"" + geneSymbol + "\");";
                geneLinkString = "<a class='grid-link' title='Filter to " + geneSymbol + "' href='" + filterGeneLink + "'><div class='grid-link-icon GeneListNode'></div></a>";
                geneLinkString += " <a class='left' target='_blank' title='View gene in new window' href='" + Urls.view_gene_symbol(geneSymbol) + "'>" + geneSymbol + "</a> ";
            } else {
                // not left
                geneLinkString += " <a target='_blank' title='View gene in new window' href='" + Urls.view_gene_symbol(geneSymbol) + "'>" + geneSymbol + "</a> ";
            }
            geneSymbolLinks.push(geneLinkString);
        }
        columnString = geneSymbolLinks.join();
    }
    return columnString;
}

function geneSymbolLink(geneSymbol, options) {
    let filterChildLink = isNodeVisible(options); // don't create kids for analysis wide tag nodes
    return _geneSymbolLink(geneSymbol, filterChildLink);
}

function geneSymbolNewWindowLink(geneSymbol) {
    return _geneSymbolLink(geneSymbol, false);
}


function showTagAutocomplete(variantId) {
    let container = $("#tag-entry-container-" + variantId);
    let addTagButton = $(".show-tag-autocomplete", container.parent());
    let nodeId = container.parents("#node-data-container").attr("node_id");
    
    addTagButton.hide();
    container.load(Urls.tag_autocomplete_form(), function() {
        var tagSelect = $("select#id_tag", container);
        tagSelect.change(function() {
            var tag = $(this).val(); 
            if (tag) {
                var successFunc = function() {
                    var vtHtml = getVariantTagHtml(variantId, tag);
                    var newTag = $(vtHtml);
                    newTag.click(tagClickHandler);
                    container.parent().append(newTag);
                    container.empty();
                    addTagButton.show();
                };
                addVariantTag(variantId, nodeId, tag, successFunc);
            }
        });
        tagSelect.select2('open');
    });

}


function getVariantTagHtml(variantId, tag) {
    return "<span class='grid-tag tagged-" + tag + "' title='Tagged as " + tag + "' variant_id='" + variantId + "' tag_id='" + tag + "'><span class='user-tag-colored'>" + tag + "</span></span>";
}


// This is driven entirely off variantTags (not passed through SQL->JQGrid)
// This is so we can add/remove tags without wrecking cache  
function tagsFormatter(tagsCellValue, a, rowData) {
    var variantId = rowData['id'];
    var tagHtml = "<a class='show-tag-autocomplete' href='javascript:showTagAutocomplete(" + variantId + ")'><span class='add-variant-tag' title='Tag variant..'></span></a>";
    tagHtml += "<span id='tag-entry-container-" + variantId + "'></span>"; 

    var aWin = getAnalysisWindow();
    var tagList = aWin.variantTags[variantId];
    if (tagList) {
        for (var i=0 ; i<tagList.length ; ++i) {
            var tag = tagList[i];
            tagHtml += getVariantTagHtml(variantId, tag);
        }        
    }
    return tagHtml;
}


function gnomADVariant(rowData) {
    var chrom = rowData["locus__contig__name"];
    if (chrom.startsWith("chr")) {
        chrom = chrom.substr(3);
    }
    return [chrom, rowData["locus__position"], rowData["locus__ref"], rowData["alt"]].join("-");
}


function gnomadFilteredFormatter(gnomadFilteredCellValue, a, rowData) {
    var gnomadFilteredString = '';
    if (gnomadFilteredCellValue !== null) {
        var filterDiv = $("<div/>").addClass("gnomad-flag-label");
        if (gnomadFilteredCellValue) {
            filterDiv.addClass("gnomad-flagged");
            filterDiv.text("Fail");
        } else {
            filterDiv.text("Pass");
        }
        var url = "http://gnomad.broadinstitute.org/variant/" + gnomADVariant(rowData);
        var gnomADLink = $("<a />").addClass("gnomad-link").attr({"href" : url, "target" : "_blank", "title" : "View in gnomAD"});
        gnomADLink.append(filterDiv);
        gnomadFilteredString = gnomADLink.get(0).outerHTML;
    }
    return gnomadFilteredString;
}


jQuery.extend($.fn.fmatter , {
    'detailsLink' : detailsLink,
    'tagsFormatter' : tagsFormatter,
    'clinvarLink' : clinvarLink,
    'cosmicLink' : cosmicLink,
    'omimLink' : omimLink,
    'geneSymbolLink' : geneSymbolLink,
    'geneSymbolNewWindowLink' : geneSymbolNewWindowLink,
    'gnomadFilteredFormatter' : gnomadFilteredFormatter,
});


// We need to do this, so that we don't send up a changing timestamp and thus never get cached
function deleteNdParam(postData) {
    var myPostData = $.extend({}, postData); // make a copy of the input parameter
    myPostData._filters = myPostData.filters;
    delete myPostData.nd;
    return myPostData;
}

// FIXME: Duplicated in jqgrid.html
function setRowChangeCallbacks(grid, gridName) {
	$(".ui-pg-selbox").change(function() {
		var gridRows = $(this).val();
		var data = 'grid_name=' + gridName + '&grid_rows=' + gridRows;
		$.ajax({
		    type: "POST",
		    data: data,
		    url: Urls.set_user_row_config(),
		});
	});
}


function tagClickHandler() {
    var gridTag = $(this);
    var innerSpan = $(".user-tag-colored", gridTag);
    function removeClickHandler() {
        var tagId = gridTag.attr('tag_id');
        var variantId = gridTag.attr('variant_id');
        var removeTagCallback = function() {
            gridTag.remove();
        };
        removeVariantTag(variantId, tagId, removeTagCallback);
    }
    deleteItemClickHandler(gridTag, innerSpan, removeClickHandler);
}


// This is always kicked off after grid is loaded (after passed in function gridComplete)
function gridCompleteExtra() {
    $(".grid-tag").click(tagClickHandler);

    // We want to be able to right click to open full screen link new tab
    // but normal click does JS / load() call to open in the editor.
    var variantLink = $('a.variant-link');
    variantLink.on("contextmenu", setFullscreenVariantLink);
    variantLink.on("mouseup", setFullscreenVariantLink);
    variantLink.on('click', restoreVariantLink);
    variantLink.on('mouseout', restoreVariantLink);

}



function setupGrid(config_url, nodeId, versionId, unique_code, gridComplete, gridLoadError, on_error_function) {
	$(function () {
    	$.getJSON(config_url, function(data) {
			var errors = data["errors"];
    		if (errors) {
				on_error_function(errors);
    		} else {
				var postData = data["postData"] || {};
				// TODO: From issue #1041 6/6/2018 - remove this when nodes config cache expires in 1 week. 
                if (typeof postData["node_id"] == "undefined") {
                    postData["node_id"] = nodeId;
                }
				// end obsolete code... 
				
				data["postData"] = postData;
				data["serializeGridData"] = deleteNdParam;
				data["shrinkToFit"] = false;

				var pagerId = '#pager-' + nodeId;
				data["pager"] = pagerId;
				data["gridComplete"] = function() {
				    gridComplete();
				    gridCompleteExtra();
				};
				data["loadError"] = gridLoadError;
	
			    var grid = getGrid(nodeId, unique_code);
			    grid.jqGrid(data).navGrid(pagerId,
	                	{add: false, edit: false, del: false, view: false, search:false},
			       		{}, // edit options
			        	{}, // add options
			       	 	{}, // del options 
			        	{ multipleSearch:true, closeOnEscape:true }, // search options 
			        	{} // view options 
		        	);

				setRowChangeCallbacks(grid, data["caption"])

		        grid.jqGrid(
		            'navButtonAdd', pagerId, {
		            caption : "VCF",
		            buttonicon : "ui-icon-arrowthickstop-1-s",
		            onClickButton : function() {
		            	export_grid(nodeId, unique_code, 'vcf');
		            },
		            position : "first",
		            title : "Download as VCF",
		            cursor : "pointer"
	        	}).jqGrid(
		            'navButtonAdd', pagerId, {
		            caption : "CSV",
		            buttonicon : "ui-icon-arrowthickstop-1-s",
		            onClickButton : function() {
		            	export_grid(nodeId, unique_code, 'csv');
		            },
		            position : "first",
		            title : "Download as CSV",
		            cursor : "pointer"
		        });
			}
	    });
	});
}

function gridLoadError(jqXHR, textStatus, errorThrown) {
    var errorMessage = errorThrown;
    var rj = jqXHR.responseJSON;
    if (rj) {
        if (rj.message) {
            errorMessage = rj.message;
        }
    }

    var ec = $("#error-container");
    ec.empty();
    ec.html("<ul class='messages'><li class='error'>Grid failed to load due to: " + errorMessage + "</li></ul>");
    $("#node-data-container").empty();
    hideLoadingOverlay();
}


/**
 * Created by peyton on 2/18/16.
 */
$( document ).ready(function() {
    $("#runnerSearch").select2({
        ajax: {
            url: "http://www." + location.hostname + ":8983/solr/runr.runners/suggest",
            dataType: "jsonp",
            jsonpCallback: 'callback',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    wt: 'json',
                    'json.wrf': "callback"
                };
            },
            processResults: function (data, params) {
                if (data.spellcheck.suggestions.length > 0) {
                    suggestions = []
                    $.each(data.spellcheck.suggestions[1].suggestion, function (i, v) {
                        suggestions.push({
                            "id": i,
                            "suggestion": v
                        })
                    });
                    return {
                        results: suggestions,
                    };
                }
                else {
                    return {
                        results: []
                    }
                }
            },

            cache: true,

        },
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        minimumInputLength: 1,
        placeholder:'Search For Runner By Name',
        templateResult: suggestionFormat, // omitted for brevity, see the source of this page
        templateSelection: suggestionSelectionRepo // omitted for brevity, see the source of this page
    });

    function suggestionFormat(suggestions) {
        if (suggestions.loading) return "Loading"
        if (suggestions != undefined) {
            var markup = "<div class='select2-result-suggestion'><b>" + suggestions.suggestion + "</b></div>";
            return markup;
        }
        return ""
    }

    function suggestionSelectionRepo(suggestions) {
        return suggestions.suggestion || 'Search For Runner By Name'
    }

    $("#runnerSearch").on("select2:select", function (e) {
        var selection = $($(this)).select2('data')
        if (selection.length == 1) {
            searchForRunner(selection[0].suggestion)
        }
    });

    function searchForRunner(runnerName) {
        $.ajax({
            'url': '/search_for_runner',
            'data': {
                'query': runnerName
            },
            success: function (data) {
                runner_object = JSON.parse(data);
                $("#runner_weight").text("Weight:" + runner_object.weight);
                $("#runner_name").text(runner_object.given_name);
                $("#runner_average_speed").text("Average Speed:" + runner_object.average_speed + " Km/hr");
                $("#runner_age").text("Age:" + runner_object.age)
            }
        })
    }
});
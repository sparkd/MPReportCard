App.module('Search', function (Search) {
    Search.SearchView = Marionette.ItemView.extend({
        template: _.template('<form role="search" id="search-form">\
        <input class="form-control" placeholder="<%= placeholder %>">\
        <span class="glyphicon glyphicon-search" aria-hidden="true"></span>\
        </form>'),
        templateHelpers: function () {
            return {
                placeholder: this.options.placeholder
            };
        },
        onRender: function () {
            this.$('input').autocomplete({
                serviceUrl: function (q) {
                    // Redirect to postcode if string contains number
                    if (q.length > 2 && q.match(/\d+/g) != null) {
                        return "http://127.0.0.1:8931/postcode"
                    } else {
                        return "http://127.0.0.1:8931/mp"
                    }
                },
                dataType: "jsonp",
                paramName: 'q',
                ajaxSettings: {
                    jsonp: 'json.wrf'
                },
                minChars: 2,
                preserveInput: true,
                showNoSuggestionNotice: true,
                noSuggestionNotice: 'Sorry, no MPs found',
                onSearchStart: function (query) {
                    if (query.q.length > 2 && query.q.match(/\d+/g) != null) {
                        // Postcode only search
                        query.q = 'postcode:' + query.q.replace(' ', '')
                    } else {
                        // Wrap the default query in brackets to handle the spaces
                        query.q = '(' + query.q + ')'
                    }
                    return query
                },
                transformResult: function (response) {
                    // Format the data we've received from SOLR

                    // We get two responses - one for the MPs, another for postcodes
                    // So map them differently if we get the grouped response
                    // Or Just the normal one
                    if (_.isUndefined(response.grouped)) {
                        return {
                            suggestions: $.map(response.response.docs, function (item) {
                                return { "value": item.name + ' (' + item.constituency + ')', data: item.id};
                            })
                        };
                    } else {
                        return {
                            suggestions: $.map(response.grouped.member_id.groups, function (item) {
                                return { "value": item['doclist']['docs'][0]['_name'] + ' (' + item['doclist']['docs'][0]['_constituency'] + ')', "data": item['groupValue'] }
                            })
                        };
                    }
                },
                onSelect: function (suggestion) {
                    this.value = ''
                    Backbone.history.navigate('mp/' + suggestion.data, { trigger: true, replace: true});
                },
                onSearchError: function (query, jqXHR, textStatus, errorThrown) {

                    if(!($(this).siblings('.autocomplete-error').length)){
                        $(this).after($('<div class="autocomplete-error"></div>')
                            .html('Sorry, there was an error searching for MPs.  Please try again later.')
                        )
                    }


                }

            })

        }
    });
});

// Add the search box to the search bar
App.addInitializer(function () {
    search = new App.Search.SearchView({placeholder: 'Find an MP'})
    App.search.show(search)
});
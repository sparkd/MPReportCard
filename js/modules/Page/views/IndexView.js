App.module('Page', function (Page) {
    Page.IndexView = Marionette.Layout.extend({
        className: 'home',
        template: '#index-page',
        regions: {
            search: "#home-search"
        },
        onShow: function () {
            this.search.show(new App.Search.SearchView({placeholder: 'Enter MP\'s name, constituency or postcode'}))
        },
        onRender: function () {
            // Make no page active
            $('#navbar-collapse li').removeClass('active');
            $('body').addClass('no-footer');
            window.scrollTo(0,0);
        },

        remove: function () {
            $('body').removeClass('no-footer');
        }
    });
});
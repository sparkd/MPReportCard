App.module('Page', function (Page) {
    Page.AboutView = Marionette.ItemView.extend({
        className: 'about',
        template: '#about-page',
        regions: {
            search: "#home-search"
        },
        onRender: function () {
            // Make mp page item active
            $('#navbar-collapse li').removeClass('active');
            $('#navbar-collapse li a[href="#about"]').parent().addClass('active');
            window.scrollTo(0,0);
        }
    });
});
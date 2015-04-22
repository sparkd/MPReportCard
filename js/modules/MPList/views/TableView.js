App.module('MPList', function (MPList) {
    MPList.TableView = Marionette.CompositeView.extend({
        className: 'mp-list',
        template: '#mplist-table',
        itemView: MPList.RowView,
        itemViewContainer: '[data-item-view-container]',
        emptyView: MPList.EmptyView,
        onRender: function () {
            window.scrollTo(0,0);
            // Make mp page item active
            $('#navbar-collapse li').removeClass('active');
            $('#navbar-collapse li a[href="#mp"]').parent().addClass('active');
            // Add table sort
            this.$('table').stupidtable();
            this.$('table').find("th.mp-name").click();
        }
    });
});
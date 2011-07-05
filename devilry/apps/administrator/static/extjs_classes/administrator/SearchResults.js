/** A grid containing search results. */
Ext.define('devilry.administrator.SearchResults', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administratorsearchresults',

    initComponent: function() {
        Ext.apply(this, {
            width: 600,
            margin: {bottom: 20},
            //height: 150,
            frame: false,
            //title: false,
            hideHeaders: true,
            columns: [{
                header: 'Nodes', dataIndex: 'long_name', flex: 1,
                renderer: this.formatRowWrapper
            }]
        });
        this.callParent(arguments);
    },

    formatRowWrapper: function(value, p, record) {
        return this.formatRow(record);
    },

    formatRow: function(record) {
        return this.getFormattedRow(
            record.get('long_name'),
            record.get('short_name'));
    },

    getFormattedRow: function(title, subtitle) {
        return Ext.String.format(
            '<div class="long_name">{0}</div><div class="short_name unimportant">{1}</div>',
            title, subtitle);
    },

    listeners: {
        selectionchange: function(view, selections, options) {
            //this.deselectAll();
        }
    },

    deselectAll: function() {
        Ext.each(this.ownerCt.items.items, function(grid, index, resultgrids) {
            grid.getSelectionModel().deselectAll();
        });
    }
});

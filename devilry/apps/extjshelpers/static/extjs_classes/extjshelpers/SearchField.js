/** A textfield for searching.
 *
 * */
Ext.define('devilry.extjshelpers.SearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.searchfield',
    fieldCls: 'widget-searchfield',

    config: {
        /**
         * @cfg
         * Delay before a search is performed in milliseconds. Defaults to 500.
         * The search is not performed if the user changes the input text before
         * ``searchdelay`` is over.
         */
        searchdelay: 500
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
        this.addEvents('emptyInput');
        this.addEvents('newSearchValue');
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            emptyText: 'Search for anything...',
            listeners: {
                scope: this,
                specialKey: function(field, e) {
                    me.handleSpecialKey(e);
                },

                change: function(field, newValue, oldValue) {
                    me.handleChange(newValue);
                }
            }
        });
        this.callParent(arguments);
    },

    triggerSearch: function(value) {
        var currentValue = this.getValue();
        var noNewInput = value == currentValue;
        if(noNewInput) {
            this.fireEvent('newSearchValue', value);
        }
    },

    handleSpecialKey: function(e) {
        if(e.getKey() == e.ENTER) {
            this.fireEvent('newSearchValue', this.getValue());
        } else if(e.getKey() == e.ESC) {
            this.fireEvent('emptyInput');
        }
    },

    handleChange: function(newValue) {
        var me = this;
        if(Ext.String.trim(newValue) == "") {
            this.fireEvent('emptyInput');
        } else {
            Ext.Function.defer(function() {
                me.triggerSearch(newValue);
            }, this.searchdelay);
        }
    }
});

var panel;

var settings = new Ext.form.FormPanel({
    fullscreen: true,
    dockedItems: [
        {
            dock: 'top',
            xtype: 'toolbar',
            title: 'Settings',
            items: [ { text: 'Cancel', handler: function() { panel.setActiveItem(0); } } ]
        }
    ],
    items: [
        {
            xtype: 'numberfield',
            name : 'age',
            label: 'Age'
        },
        {
            xtype: 'numberfield',
            name : 'weight',
            label: 'Weight'
        },
        {
            xtype: 'numberfield',
            name : 'budget',
            label: 'Budget'
        },
        {
            xtype: 'button',
            name: 'save',
            text: 'Save',
        }
    ]
});

var data = {
    items: [
        {
            text: 'Dates',
            items: [
                { text: 'Today', items: [] },
                { text: 'Yesterday', items: [] },
                { text: '2 Days Ago', items: [] },
                { text: '3 Days Ago', items: [] },
                { text: '4 Days Ago', items: [] },
                { text: '5 Days Ago', items: [] }
            ]
        },
        {
            text: 'About',
            items: [ { text: 'Kilo gives you easy access to your food diary.' } ]
        }
    ]
};
Ext.regModel('ListItem', {
    fields: [{name: 'text', type: 'string'}]
});
var store = new Ext.data.TreeStore({
    model: 'ListItem',
    root: data,
    proxy: {
        type: 'ajax',
        reader: {
            type: 'tree',
            root: 'items'
        }
    }
});
var nestedList = new Ext.NestedList({
    fullscreen: true,
    title: 'Kilo',
    displayField: 'text',
    store: store,
    toolbar: { ui: 'dark', items: [ { xtype: 'spacer' }, { text: 'Settings', handler: function() { panel.setActiveItem(1); } } ] }
});

var list = new Ext.Panel({
    fullscreen: true,
    items: [ nestedList ]
});


Ext.setup({
    onReady: function() {
                 panel = new Ext.Panel({
                     fullscreen: true,
                     layout: 'card',
                     items: [ list, settings ]
                 });
             }
})

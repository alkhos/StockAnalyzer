$(function() {
    $('#submit').on('click', function(e) {
        //console.log(url);
        // var url_value = '/api/intrinsicvalue?symbol=' + document.getElementById('symbol').value
        // if (document.getElementById('growth_rate')) {
        //    url_value = url_value + '&growth_rate=' + +document.getElementById('growth_rate').value
        //}
        e.preventDefault()
        $.ajax({
            url: '/api/intrinsicvalue?symbol=' + document.getElementById('symbol').value,
            success: function(data) {
                alert('Successfully called');
                console.log(data)
                $('#stock_symbol').html(data['symbol']);
                $('#intrinsic_value').html(data['intrinsic_value']);
                $('#stock_price').html(data['stock_price']);
                $('#beta').html(data['beta']);
                Plotly.newPlot('free_cash_flow_plot', JSON.parse(data['free_cash_flow_plot']));
                //Plotly.plot('free_cashflow_plot', data['free_cashflow_plot']);
            },
            error: function() {
                $("#results").html('No results found.');
            }
        });
    });
})
$(function() {
    $('#submit').on('click', function(e) {
        //console.log(url);
        var url_value = '/api/intrinsicvalue?symbol=' + document.getElementById('symbol').value
        if (document.getElementById('growth_rate')) {
            url_value = url_value + '&growth_rate=' + document.getElementById('growth_rate').value
        }
        e.preventDefault()

        $.ajax({
            url: url_value,
            beforeSend: function() {
                // Show image container
                $("#loader").show();
            },
            success: function(data) {
                console.log(data)
                    // fill in metrics
                $('#stock_symbol').html(data['symbol']);
                $('#intrinsic_value').html(data['intrinsic_value']);
                $('#stock_price').html(data['stock_price']);
                $('#beta').html(data['beta']);
                // plot total revenue
                Plotly.newPlot('total_revenue_plot', JSON.parse(data['total_revenue_plot']));
                // plot EPS
                Plotly.newPlot('eps_plot', JSON.parse(data['eps_plot']));
                // plot accounts payable
                Plotly.newPlot('accounts_payable_plot', JSON.parse(data['accounts_payable_plot']));
                // plot acccounts receivable
                Plotly.newPlot('accounts_receivable_plot', JSON.parse(data['accounts_receivable_plot']));
                // plot inventory
                Plotly.newPlot('inventory_plot', JSON.parse(data['inventory_plot']));
                // plot FCF
                Plotly.newPlot('free_cash_flow_plot', JSON.parse(data['free_cash_flow_plot']));
                // Growth Plots
                Plotly.newPlot('growth_plots', JSON.parse(data['growth_plots']));
            },
            error: function() {
                alert('Failed to retrieve data');
                $("#results").html('No results found.');
            },
            complete: function(data) {
                // Hide image container
                $("#loader").hide();
            }
        });
    });
})
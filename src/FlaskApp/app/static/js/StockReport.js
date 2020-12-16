$(function() {
    $('#submit').on('click', function(e) {
        //console.log(url);
        var url_value = '/api/intrinsicvalue?symbol=' + document.getElementById('symbol').value
        var growth_rate = document.getElementById('growth_rate');
        if (growth_rate != null && growth_rate.value != '') {
            url_value = url_value + '&growth_rate=' + growth_rate.value
        }
        var effective_tax_rate = document.getElementById('effective_tax_rate');
        if (effective_tax_rate != null && effective_tax_rate.value != '') {
            url_value = url_value + '&effective_tax_rate=' + effective_tax_rate.value
        }
        var interest_rate = document.getElementById('interest_rate');
        if (interest_rate != null && interest_rate.value != '') {
            url_value = url_value + '&interest_rate=' + interest_rate.value
        }
        e.preventDefault()

        $.ajax({
            url: url_value,
            beforeSend: function() {
                // Show image container
                $("#loader").show();
                $("#results").hide();
                $("#plots").hide();
                $("#links").show();
            },
            success: function(data) {
                console.log(data)
                    // fill in metrics
                    // intrinsic valu
                $('#stock_symbol').html(data['symbol']);
                $('#stock_name').html(data['stock_name']);
                $('#intrinsic_value').html('$' + data['intrinsic_value']);
                // modify intrinsic value color
                if (parseFloat(data['intrinsic_value']) > parseFloat(data['stock_price'])) {
                    $("#intrinsic_value_1").attr("style", "background-color:rgb(35, 196, 29);");
                    $("#intrinsic_value_2").attr("style", "background-color:rgb(35, 196, 29);");
                } else {
                    $("#intrinsic_value_1").attr("style", "background-color:rgb(230, 71, 71);");
                    $("#intrinsic_value_2").attr("style", "background-color:rgb(230, 71, 71);");
                }
                $('#stock_price').html('$' + data['stock_price']);
                $('#market_cap').html('$' + data['market_cap'] + 'M');
                $('#shares_outstanding').html(data['shares_outstanding'] + 'M');
                $('#short_term_debt').html('$' + data['short_term_debt'] + 'M');
                $('#long_term_debt').html('$' + data['long_term_debt'] + 'M');
                $('#total_liabilities').html('$' + data['total_liabilities'] + 'M');
                $('#cash').html('$' + data['cash'] + 'M');
                $('#beta').html(data['beta']);
                $('#ttm_free_cash_flow').html('$' + data['ttm_free_cash_flow'] + 'M');
                $('#gdp_growth_rate').html(data['gdp_growth_rate'] + '%');
                $('#marktet_rish_premium').html(data['marktet_rish_premium']);
                $('#risk_free_rate').html(data['risk_free_rate'] + '%');
                $('#business_interest_rate').html(data['business_interest_rate'] + '%');
                $('#income_tax_rate').html(data['income_tax_rate'] + '%');
                $('#business_growth_rate').html(data['business_growth_rate']);
                // ben graham
                $('#current_ratio').html(data['current_ratio']);
                $('#d_t_n_c_a_ratio').html(data['d_t_n_c_a_ratio']);
                $('#earning_deficits').html(data['earning_deficits']);
                $('#dividend').html(data['dividend']);
                $('#earning_growth').html(data['earning_growth']);
                $('#p_t_b_v_ratio').html(data['p_t_b_v_ratio']);
                $('#r_o_i_c').html(data['r_o_i_c']);
                $('#w_a_c_c').html(data['w_a_c_c']);
                // Peter Lynch
                $('#p_e').html(data['p_e']);
                $('#p_e_g').html(data['p_e_g']);
                $('#d_p_e_g').html(data['d_p_e_g']);
                $('#n_c_s').html(data['n_c_s']);
                $('#d_e_ratio').html(data['d_e_ratio']);
                $('#invetory_turnover').html(data['invetory_turnover']);
                $('#insider').html(data['insider']);
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
                Plotly.newPlot('growth_plots_annual', JSON.parse(data['growth_plots_annual']));
                Plotly.newPlot('growth_plots_quarterly', JSON.parse(data['growth_plots_quarterly']));
                // Links
                var yfinance = 'https://finance.yahoo.com/quote/' + data['symbol']
                $("#yfinance").attr('href', yfinance);
                var morningstar = 'https://www.morningstar.com/stocks/xnas/' + data['symbol'] + '/quote'
                $("#morningstar").attr('href', morningstar);
                var macrotrends = 'https://www.macrotrends.net/stocks/charts/' + data['symbol'] + '/' + data['stock_name'] + '/financial-statements'
                $("#macrotrends").attr('href', macrotrends);
                var annualreports = 'https://www.annualreports.com/Companies?search=' + data['symbol']
                $("#annualreports").attr('href', annualreports);
            },
            error: function() {
                alert('Failed to retrieve data');
                $("#results").html('No results found.');
            },
            complete: function(data) {
                // Hide image container
                $("#loader").hide();
                $("#results").show();
                $("#plots").show();
                $("#links").show();
            }
        });
    });
})
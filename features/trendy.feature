Feature: method length trend analysis

	Scenario: Method Length is Increasing
		Given a collection of method line data points
		And the data is trending toward longer methods
		When we ask for a trend analysis 
		Then the analysis reports a problematic trend

	Scenario: Method Length is Decreasing
		Given a collection of method line data points
		And the data is trending toward shorter methods
		When we ask for a trend analysis 
		Then the analysis reports a satisfactory trend

	Scenario: Method Length is neither Increasing or Decreasing
		Given a collection of method line data points
		And the data is consistent
		When we ask for a trend analysis 
		Then the analysis reports a satisfactory trend
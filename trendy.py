#!/usr/bin/env python3
import argparse
from collections import defaultdict, namedtuple
from dateutil import parser as duparser
import json
import pytest
import sys

# Example Output
ex = {
	"method_lines": {
	  "long": "pos",
	  "long_val": 0.13564660430125614,
	  "middle": "neg",
	  "middle_val": -0.02315474822556712,
	  "short": "neg",
	  "short_val": -0.004576938779485219
	},
	"complexity": {
	  "long": "pos",
	  "long_val": 0.01889381188298741,
	  "middle": "neg",
	  "middle_val": -0.004218355937805478,
	  "short": "pos",
	  "short_val": 0.00018921633287577471
	},
	"fan_out": {
	  "long": "pos",
	  "long_val": 0.10642814256605759,
	  "middle": "pos",
	  "middle_val": 0.007939208247217134,
	  "short": "neg",
	  "short_val": -0.014023793916072294
	}
}

RawSlopeData = namedtuple('RawSlopeData', ['y1','y2','x1','x2'])


def measure_struct():
	return {
		'raw': list(),
		'interstitial': list(),
		'trend': {
			'long': 'ukn', 'long_val': 0,
			'middle': 'ukn', 'middle_val': 0,
			'short': 'ukn', 'short_val': 0,
		}
	}


def make_raw_data(pair):
	y1 = pair[0]['mean']
	y2 = pair[1]['mean']
	x1 = duparser.parse(pair[0]['datetime']).timestamp() / 86400
	x2 = duparser.parse(pair[1]['datetime']).timestamp() / 86400
	return RawSlopeData(y1,y2,x1,x2)


def slope_of(raw_data):
	try:
		return (raw_data.y2-raw_data.y1)/(raw_data.x2-raw_data.x1)
	except ZeroDivisionError:
		return float('inf')


epsilon = 0.000000001  # todo how the hell do you know if that is a good value?

def slope_word(slope):
	if slope == float('inf'):
		return 'ukn'
	if slope > epsilon:
		return 'pos'
	if slope < (0-epsilon):
		return 'neg'
	if (0-epsilon) < slope < (0+epsilon):
		return 'sbl'


def combine_raw_data(first, second):
	return RawSlopeData(first.y1,second.y1,first.x1,second.x1)


def collect_raw_data_and_interstitial_slopes(input):
	def create_adjacent_pairs(measurments):
		sorted_measurments = sorted(measurments, key=lambda m: m['datetime'])
		return list(zip(sorted_measurments, (*sorted_measurments[1:],*[None])))[:-1]

	out = defaultdict(measure_struct)
	for measure, measurments in json.loads(input).items():
		measure_pairs = create_adjacent_pairs(measurments)
		for pair in measure_pairs:
			out[measure]['raw'].append(make_raw_data(pair))
			out[measure]['interstitial'].append(slope_of(out[measure]['raw'][-1]))
	return out


def calculate_trend_data(report):
	def add_slope(trend_block, name, left, right):
		slope = slope_of(combine_raw_data(left, right))
		trend_block['{}_val'.format(name)] = slope
		trend_block[name] = slope_word(slope)

	for measure, data in report.items():
		if len(data['raw']) > 1:
			first = data['raw'][0]
			last = data['raw'][-1]
			middle_data = data['raw'][int(len(data['raw'])/2)]
			penultimate = data['raw'][-2]
			add_slope(data['trend'], 'long', first, last)
			add_slope(data['trend'], 'middle', middle_data, last)
			add_slope(data['trend'], 'short', penultimate, last)


def do_trend_analysis(input):
	report = collect_raw_data_and_interstitial_slopes(input)
	calculate_trend_data(report)
	return report


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('inputfile')
	args = parser.parse_args()
	if args.inputfile:
		print('the input file is {}'.format(args.inputfile))
		with open(args.inputfile) as fin:
			out = do_trend_analysis(fin.read())
			result = dict()
			for measure, data in out.items():
				result[measure]=data['trend']
			print('{}'.format(json.dumps(result, indent=2, sort_keys=True)))
	else:
		print('no file specified')
		sys.exit(1)


def test_do_trend_analysis_works():
	test_data = json.dumps(
		{
			"method_lines": [
				{
					"datetime": "2017-12-21T13:42:29-05:00",
					"mean": 12.067264573991032
				},
				{
					"datetime": "2017-12-21T13:42:29-05:00",
					"mean": 12.067264573991032
				},
			]
		}
	)
	out = do_trend_analysis(test_data)

	assert 'method_lines' in out
	assert 'trend' in out['method_lines']
	assert 'long' in out['method_lines']['trend']
	assert 'middle' in out['method_lines']['trend']
	assert 'short' in out['method_lines']['trend']


def test_do_trend_analysis_reports_pos_neg_or_sbl():
	test_data = json.dumps(
		{
			"method_lines": [
				{
					"datetime": "2017-12-21T13:42:29-05:00",
					"mean": 0
				},
				{
					"datetime": "2017-12-22T13:42:29-05:00",
					"mean": 1
				},
				{
					"datetime": "2017-12-23T13:42:29-05:00",
					"mean": 2.9999999999999
				},
				{
					"datetime": "2017-12-24T13:42:29-05:00",
					"mean": 3
				}
			]
		}
	)
	out = do_trend_analysis(test_data)

	assert out['method_lines']['trend']['long'] == 'pos'
	assert out['method_lines']['trend']['middle'] == 'pos'
	assert out['method_lines']['trend']['short'] == 'pos'


def test_measure_struct_default_values():
	assert measure_struct() == {
		'raw': list(),
		'interstitial': list(),
		'trend': {
			'long': 'ukn', 'long_val': 0,
			'middle': 'ukn', 'middle_val': 0,
			'short': 'ukn', 'short_val': 0,
		}
	}


def test_make_raw_data_pair_converts_input_to_RawSlopeData():
	pair = (
		{'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, 
		{'mean':2,'datetime':'2017-09-22T17:11:13-04:00'}
		)

	raw_data = make_raw_data(pair)

	assert type(raw_data) is RawSlopeData
	assert raw_data.y1 == pair[0]['mean']
	assert raw_data.y2 == pair[1]['mean']
	# todo how do I get to hours?
	assert raw_data.x1 == duparser.parse(pair[0]['datetime']).timestamp() / 86400
	assert raw_data.x2 == duparser.parse(pair[1]['datetime']).timestamp() / 86400


def test_make_raw_data_requires_a_pair():
	with pytest.raises(TypeError):
		make_raw_data(None)


def test_make_raw_data_requires_a_whole_pair_left():
	with pytest.raises(TypeError):
		make_raw_data(({'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, None))


def test_make_raw_data_requires_a_whole_pair_right():
	with pytest.raises(TypeError):
		make_raw_data((None, {'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}))


def test_make_raw_data_date_time_must_be_parsable_valid_date():
	with pytest.raises(duparser.ParserError):
		make_raw_data(
			(
				{'mean':1,'datetime':'2016-31-22T17:11:13-04:00'}, 
				{'mean':2,'datetime':'2017-09-22T17:11:13-04:00'}
			)
		)


def test_make_raw_data_date_time_must_be_parsable_not_a_date():
	with pytest.raises(duparser.ParserError):
		make_raw_data(
			(
				{'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, 
				{'mean':2,'datetime':'this is not a parsable date'}
			)
		)


def test_slope_of_returns_the_slope_zero_if_the_mean_does_not_change():
	raw_data = make_raw_data(
			(
				{'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, 
				{'mean':1,'datetime':'2016-09-22T18:11:13-04:00'}
			)
		)
	assert slope_of(raw_data) == 0 


def test_slope_of_returns_the_slope_one_if_the_mean_increased_by_one_per_day():
	raw_data = make_raw_data(
			(
				{'mean':0,'datetime':'2016-09-22T17:11:13-04:00'}, 
				{'mean':1,'datetime':'2016-09-23T17:11:13-04:00'}
			)
		)
	assert slope_of(raw_data) == 1 

def test_slop_of_returns_the_slope_minus_one_if_the_mean_decreases_by_one_per_day():
	raw_data = make_raw_data(
			(
				{'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, 
				{'mean':0,'datetime':'2016-09-23T17:11:13-04:00'}
			)
		)
	assert slope_of(raw_data) == -1 


def test_combine_raw_data_merges_two_raw_datas():
	first = RawSlopeData(1,2,3,4)
	second = RawSlopeData(5,6,7,8)
	expected = RawSlopeData(first.y1,second.y1,first.x1,second.x1)

	combined = combine_raw_data(first,second)

	assert combined == expected


def test_combine_raw_data_requires_first_arg():
	first = None
	second = RawSlopeData(5,6,7,8)

	with pytest.raises(AttributeError):
		combine_raw_data(first,second)


def test_combine_raw_data_requires_second_arg():
	first = RawSlopeData(1,2,3,4)
	second = None

	with pytest.raises(AttributeError):
		combine_raw_data(first,second)

def test_slope_word_sez_pos_when_input_gt_zero():
	assert slope_word(epsilon*10) == 'pos'


def test_slope_word_sez_neg_when_input_lt_zero():
	assert slope_word(-epsilon*10) == 'neg'


def test_slope_word_sez_sbl_when_input_near_zero():
	assert slope_word(epsilon/10) == 'sbl'
	assert slope_word(0) == 'sbl'
	assert slope_word(-epsilon/10) == 'sbl'


def test_slop_word_sez_ukn_when_input_is_inf():
	assert slope_word(float('inf')) == 'ukn'

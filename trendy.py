#!/usr/bin/env python3
import argparse
from collections import defaultdict, namedtuple
from dateutil import parser as duparser
import json
import pytest
import sys

def analyze(data):
	result = 'undetermined'
	return result

def measure_struct():
	return {
		'raw': list()
	}


def collect_raw_data(input):
	report = defaultdict(measure_struct)
	for measure, measurments in json.loads(input).items():
		report[measure]['raw'] = list()
		for measurment in measurments:
			report[measure]['raw'].append((duparser.parse(measurment['datetime']).timestamp() / 86400, measurment['mean']))
	return report


def do_trend_analysis(input):
	report = collect_raw_data(input)
	return report


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('inputfile')
	args = parser.parse_args()
	if args.inputfile:
		with open(args.inputfile) as fin:
			out = do_trend_analysis(fin.read())
			# print(out)
			print(json.dumps(out, indent=2, sort_keys=True))
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
					"mean": 0,
					"stdev": 1,
				},
				{
					"datetime": "2017-12-22T13:42:29-05:00",
					"mean": 1,
					"stdev": 1,
				},
				{
					"datetime": "2017-12-23T13:42:29-05:00",
					"mean": 2.9999999999999,
					"stdev": 1,
				},
				{
					"datetime": "2017-12-24T13:42:29-05:00",
					"mean": 3,
					"stdev": 1,
				}
			]
		}
	)
	out = do_trend_analysis(test_data)

	assert out['method_lines']['trend']['long'] == 'positive'
	assert out['method_lines']['trend']['middle'] == 'positive'
	assert out['method_lines']['trend']['short'] == 'positive'


def test_measure_struct_default_values():
	assert measure_struct() == {
		'raw': list()
	}


def test_make_raw_data_pair_converts_input_to_RawData():
	pair = (
		{'mean':1,'datetime':'2016-09-22T17:11:13-04:00'}, 
		{'mean':2,'datetime':'2017-09-22T17:11:13-04:00'}
		)

	raw_data = make_raw_data(pair)

	assert type(raw_data) is RawData
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


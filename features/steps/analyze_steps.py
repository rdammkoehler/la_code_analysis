from os import getcwd
from trendy import analyze

@given(u'a collection of method line data points')
def step_impl(context):
  context.data_points = list()


@given(u'the data is trending toward longer methods')
def step_impl(context):
  context.data_points.extend([(0,0),(1,1),(2,2),(3,3),(4,4)])


@when(u'we ask for a trend analysis')
def step_impl(context):
  context.result = analyze(context.data_points)


@then(u'the analysis reports a problematic trend')
def step_impl(context):
  assert context.result == 'problematic'


@given(u'the data is trending toward shorter methods')
def step_impl(context):
  context.data_points.extend([(0,4),(1,3),(2,3),(3,1),(4,0)])


@then(u'the analysis reports a satisfactory trend')
def step_impl(context):
  assert context.result == 'satisfactory'


@given(u'the data is consistent')
def step_impl(context):
  context.data_points.extend([(0,1),(1,1),(2,1),(3,1),(4,1)])

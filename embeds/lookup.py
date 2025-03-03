import dataclasses

from commons.models.base import Model

model_lookup = {}
subclasses = []
subclasses_next = [Model]


def setup():
	global subclasses, subclasses_next, model_lookup
	while subclasses_next:
		temp = []
		for _klass in subclasses_next:
			temp.extend(_klass.__subclasses__())
		subclasses.extend(subclasses_next)
		subclasses_next = temp

	for model in subclasses:
		if dataclasses.is_dataclass(model):
			try:
				model_lookup[model._klass] = model
			except AttributeError:
				pass


def object_hook_ability(dct: dict[str, any]):
	if '_klass' in dct:
		name = dct.pop("_klass")
		return model_lookup[name](**dct)
	return dct

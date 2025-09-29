# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class RemittanceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		description: DF.Data
		item_type: DF.Literal["Tithe", "Offering to Field", "Camp Meeting Offering", "Special Offering", "Other"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		percentage: DF.Percent
		period_from: DF.Date | None
		period_to: DF.Date | None
	# end: auto-generated types

	pass

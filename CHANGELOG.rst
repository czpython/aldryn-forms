Changelog
=========

1.0.3 (2015-12-08)
------------------
* Fixes critical bug with nested plugins.

1.0.2 (2015-12-08)
------------------
* Fixes plugin ordering bug.
* Fixes TypeError on some fields because of the validator.
* Marks some strings as translatable.

1.0.1 (2015-11-26)
------------------
* Allows for custom forms to opt out of a success message.

1.0.0 (2015-11-03)
------------------
* Stable release

0.6.0 (2015-10-14)
------------------
* adds validator on max_length fields
* cms 3.1 migration compatibility fix

0.5.1 (2015-09-29)
------------------
* cms 3.1 compatibility fix

0.5.0 (2015-08-19)
------------------
* added django 1.7 & 1.8 compatibility
* fixes AttributeError with orphan plugins

0.4.1 (2015-07-10)
------------------
* added notification config class to support custom text variables
* allow disabling email html version
* allow hiding of email body txt format field
* fixed bug with serialized boolean value

0.4.0 (2015-07-02)
------------------
* added email notification contrib app which includes new email notification form
* added html version to admin notification email text
* changed the users_notified field to a text field to support non user recipients
* hides the captcha field/value from serialized data
* cleaned up field serialization logic.

0.3.3 (2015-05-29)
------------------
* added support for default values in selectfields, multiselectfields and radioselects (bootstrap).
* fixed empty values in select options

0.3.2 (2015-05-19)
------------------
* bootstrap3 support
* added bootstrap markup templates for all field-types

0.3.0 (2015-03-02)
------------------
* multi-boilerplate support
* new requirement: aldryn-boilerplates (needs configuration)

15/4:

got a debugger on a running instance of hass, its got an f5 experience!
(its a great vscode setup I might have to look at how they've done this at some point)

connected to my tuya account
(I always forget its the developer account id/secret + the APP (not the dev cloud) username/pass)

I gained the understanding that a lot of method calls actually happen by passing a callback to hass.async_add_executor_job(), this makes the code much easier to follow
(I should look up the doco on that code)

I watched a call via TuyaOpenAPI to "/v1.0/users/{self.api.token_info.uid}/devices" return the aircon and tv devices with the categories `infrared_ac` and `infrared_tv` respectively. The IR hub comes through with the category `qt`

going to keep debugging to see how it fails to register these as a known device type, perhaps I need to create a new device type to match these?

A call via TuyaOpenAPI to "/v1.0/devices/{device_id}/specifications" for the airconditioner came back with a bunch of info about available commands and status, whereas the same call for the IR came back with a message that it is not supported. I think this means there is nothing to do with the hub itself in hass but I should be able to use the info I got about the aircon to populate a device?

async_setup_entry seems to register a bunch of unsupported devices and then calls async_forward_entry_setups with a set of platforms

16/4:

what does async_forward_entry_setups do?
    can't tell from the docs
    what do they mean by component exactly?
    I think they mean an entity
    I put a debugger on light.async_setup_entry and it was called
    It looks like each entitires async_setup_entry is called. In light it checks the entire device manager device map for entities that match a hardoded list of constants
    If it matches it adds the entity

Tuya entities are very simple you just need to use the base class to check states and get commands.

What is the category for the device maps for the tv and the aircon? infrared_tv & infrared_ac

Is there an entity that matches the tv and aircon commands and states well? If not how would you model it?

    Maybe I can use remote to model anything that comes through. It looks like it might map a dynamic list of commands?

    infrared_ac looks like it might map pretty well to the climate entity, lets check the commands.
        Yep:
            M -> Mode: heat or cool
            F -> Fan_mode: low, medium, high
            T -> Target_Temp: 18-30
            Poweron
            Poweroff

        Looks like you can set supported modes from the total set of modes too.

     infraed_tv might map to a remote of a media player. Neither are supported by tuya



What does a programmable entity look like? Could I just hardcode my entity for now? Maybe a remote


what exactly are the platforms passed to async_forward_entry_setups? https://developers.home-assistant.io/docs/creating_platform_index?_highlight=platform

what does a config entry do? https://developers.home-assistant.io/docs/config_entries_index/

is it the case that the tv and aircon are not in the supported list of platforms is that all I need to do?
    infrared_ac can match climate
    not sure about tv

do we need to create a specific tuya entity for an aircon and a tv?
    climate can be adapted to infrared_ac
    not sure about tv

do I just need to read the whole documentation before I keep coding?
    doesn't look like it

Understand next:
    The climate tuya implementation
        - Are the commands and states that come through with the device entries in the device_map the commands I would need to send via base entities self._send_command and the proprties I would need to keep track of as properties?
            - No they dont look like the strings match
        - If I keep state as properties that means I dont need to check the state coming back through the device:
            - Can I check state via the base class?
            - Do I even really need to considering the aircon remote is probably using a desired state model. Are the commands all setting a desired state?
                - Yes it looks like climate sets a desired state
        - Is climate at good fit?
            - It looks like climate is expecting a specific set of DPCodes from the tuya device. I'm not sure if thr IR device is going to have them. Might be better to creata a new climate device based of the ir devices function list rather than DPCodes?
    The remote entity
        Could this check state? Cos the climate entity doesn't check state.
            Anything can check state if tuya provides it https://developers.home-assistant.io/docs/core/entity/#updating-the-entity
    Entities in general

I think I'm going to try to confirm a remote could be a good fit for any infared_xx device that comes back.

Some ideas for working out what it might look like.
    - Have any other integrations implemented a remote? Do they have tests to show what data the integration provides to configure the remote?
    - Is there a chat room I could join do talk to someone about it? Either a HASS developers or Tuya developers or both?
    - Can I open a PR or issue on the HASS repo to get advice?

Had a look at the harmony remote. I think I can imagine how to implement it:
- Extend the Remote class
- Keep a list of available activities in properties on the class
- Initialise the activity list from the config entry
- Send commands via the api
- Open questions:
    - What is all this device connection/disconnectio/removal etc, work out the lifecycle
    - Work out all the state changes, maybe do a state diagram
    - Are the commands to send the text strings I get from the config entry?
    - How do I know indicate when a command is in progress or success failed?
    - Can I indicate the state of the thing I am controlling? Maybe with assumed state due to the fact the commands will be in the form of a desired state?

Next steps:
    - Work out how to run tests
    - Read how to write tests (via the hass public api only, though I could write unit tests to help me implement I'm sure)
    - Spike the implementation
    - TDD the implementation

20/4

Know how to run tests https://developers.home-assistant.io/docs/development_testing?_highlight=test#running-a-limited-test-suite

Tests to write:
- setup entry creates correct devices
    - Can get the device by `hass.states.get("remote.<name>")`
    - Will be None by default
- setup entry _populates activities_ (what does this actually mean? Is this going to be entity state?)
    - Can get attributes by `hass.states.get("remote.<name>").attributes.get("activities")`
- _sends command to the tuya api_ (what does this mean, I think I want to assert on the tuya api, but how do I trigger the command?)
    - I think so it looks like `TuyaDevice.function["<function>"]` has a `code` property and `values` to send. Looking at the lights it looks like these values match the entity descriptions which the lights use to find the code to send to tuya

Still relevant questions:
- What is all this device connection/disconnectio/removal etc, work out the lifecycle
- Work out all the state changes, maybe do a state diagram
- Are the commands to send the text strings I get from the config entry?
- How do I know indicate when a command is in progress or success failed?
- Can I indicate the state of the thing I am controlling? Maybe with assumed state due to the fact the commands will be in the form of a desired state?
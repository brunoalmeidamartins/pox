# Import all of Scapy's code so we can use it as a library (rather than the runtime environment it also supports)
# I don't like this "import *" and would much rather import Scapy functionality under a namespace but I'm fairly
# new to the library and my initial efforts seemed to throw some errors so I just copied this from other sources.
# Don't judge me.
from scapy.all import *


# For non python people, this is just python's, somewhat strange, way of saying
# "If this file is being executed and not just imported into another file"
if __name__ == '__main__':

    # tap0 is now the file descriptor for the opened /dev/tap0, which we can read and write to
    tap0 = os.open('/dev/tap0', os.O_RDWR)

    # Run loop indefinitely
    while 1:
        # Select is an operating system level function which python makes available to us.
        # It takes 3 lists of file descriptors (or objects which make a file descriptor easy to find),
        # and waits until one of them is ready for I/O.
        # The first parameter are FDs it will wait for until they're ready to be read from.
        # The second are FDs it will wait for until they're ready to be written to.
        # The third is for "exceptional conditions" which you can read more about in python's documentation
        # Since we're only concerned with waiting until there's data to be read, we only pass in the first parameter
        sel = select.select([tap0], [], [])
        # We check that the tap0 FD is, in fact, what is ready to be read from.
        # Completely unnecessary in this case for us to check this as tap0 is the only thing we're monitoring
        # but it's a good habit, I feel.
        if tap0 in sel[0]:
            # MTU, the "Maximum Transmission Unit", it's the largest size a frame or packet
            # can be and is set for us by Scapy.
            frame = os.read(tap0, MTU)
            # Convert the raw bytes we read into a Scapy class
            frame = Ether(frame)

            # If the message we pulled off the device is an ARP request
            if isinstance(frame.payload, ARP) and frame.payload.op == ARP.who_has:
                # This is admittedly a bit strange and deserves special note.
                # This is saying, take the MAC address that sent the request and set it as the response's,
                # src. You may be wondering, very accurately, why we're doing this rather than using RandMac
                # to generate a completely different MAC address. Along with ARP requests for things like the router,
                # OSX will also send an ARP request for the device's *own* IP address. If it receives a different MAC
                # address than what has sent, it naturally assumes that there are two different machines trying to use
                # the same IP address and throw an error.
                #
                # What we *should* be doing is logically determining when we generate a new MAC address and when we
                # use the requesting MAC address. But that would take knowledge and work and just sending back the
                # requester's MAC address seems to work without error for our purposes. Until it inevitably comes back
                # to bite us in the ass at some point, of course.
                src_mac_addr = frame.payload.hwsrc

                # Here we generate the response we'll send back down the "wire". ARP asked us "who_has this address"
                # and we're saying "That address is_at this MAC address"
                # Notice the OSI model at work here? We're specifying our Ethernet layer here first, which contains things
                # like our destination and source and append the next layer (denoted in Scapy by the '/' division symbol)
                # which contains our ARP layer of information.
                # It should also be noted that there is much more to these protocols than what is listed here, but Scapy
                # is nice enough to try to deduce those extra fields for us.
                response = Ether(dst=frame.src, src=src_mac_addr) / ARP(op=ARP.is_at,
                                                                        hwsrc=src_mac_addr,
                                                                        psrc=frame.payload.pdst,
                                                                        hwdst=frame.payload.hwsrc,
                                                                        pdst=frame.payload.psrc)

                # Write the response into the /dev/tap0 where it will be injected into the operating system's network
                # stack and treated as if it came from an organic source.
                os.write(tap0, str(response))

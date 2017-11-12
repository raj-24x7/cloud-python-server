#python3

# RAJ KUMAR - 20145117

import smtplib
import socket
import base64
import email
import email.message
import email.header
import email.mime.multipart
import email.mime.text

def recvline(sock):
    """Receives a line. To read Socket msg"""
    stop = 0
    line = ''
    while True:
        i = sock.recv(1)
        if i.decode('UTF-8') == '\n': stop = 1
        line += i.decode('UTF-8')
        if stop == 1:
            print('Stop reached.')
            break
    print('Received line: %s' % line)
    return line

class ProxySMTP(smtplib.SMTP):
    """Connects to a SMTP server through a HTTP proxy."""

    def __init__(self, host='smtp.gmail.com', port=587, p_address='172.31.100.25',p_port=3128, local_hostname=None,
             p_username='edcguest', p_password='edcguest', timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Initialize a new instance.

        If specified, `host' is the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, smtplib.SMTP_PORT is used.  An SMTPConnectError is raised
        if the specified `host' doesn't respond correctly.  If specified,
        `local_hostname` is used as the FQDN of the local host.  By default,
        the local hostname is found using socket.getfqdn().

        """
        self.p_address = p_address
        self.p_port = p_port
        self.p_username = p_username
        self.p_password = p_password

        self.timeout = timeout
        self.esmtp_features = {}
        self.default_port = smtplib.SMTP_PORT

        if host:
            (code, msg) = self.connect(host, port)
            if code != 220:
                raise IOError(code, msg)

        if local_hostname is not None:
            self.local_hostname = local_hostname
        else:
            # RFC 2821 says we should use the fqdn in the EHLO/HELO verb, and
            # if that can't be calculated, that we should use a domain literal
            # instead (essentially an encoded IP address like [A.B.C.D]).
            fqdn = socket.getfqdn()

            if '.' in fqdn:
                self.local_hostname = fqdn
            else:
                # We can't find an fqdn hostname, so use a domain literal
                addr = '127.0.0.1'

                try:
                    addr = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    pass
                self.local_hostname = '[%s]' % addr

        smtplib.SMTP.__init__(self)

    def _get_socket(self, port, host, timeout):
        """ The method modified for HTTP proxy and Authentication """
        # This makes it simpler for SMTP to use the SMTP connect code
        # and just alter the socket connection bit.
        print('Will connect to:',host, port)
        print('Connect to proxy.')
        new_socket = socket.create_connection((self.p_address,self.p_port), timeout)
        # CONNECT TUNNEL
        s = "CONNECT %s:%s HTTP/1.1\r\nProxy-Authorization: Basic %s\r\n\r\n" % (port,host,base64.b64encode(str(self.p_username+":"+self.p_password).encode("utf-8")))
        s = s.encode('UTF-8')
        new_socket.sendall(s)
        #ZWRjZ3Vlc3Q6ZWRjZ3Vlc3Q= base64 for edcguest:edcguest
        print('Sent CONNECT. Receiving lines.')
        for x in range(2):
        	recvline(new_socket)
        print('Connected.')
        return new_socket

def main(receiver, message, subject, to_name):
    proxy_host = '172.31.100.25'
    proxy_port = 3128
    proxy_username = 'edcguest'
    proxy_password = 'edcguest'
    # Both port 25 and 587 work for SMTP
    conn = ProxySMTP(host='smtp.gmail.com', port=587,
                     p_address=proxy_host, p_port=proxy_port,
                     p_password=proxy_password ,p_username=proxy_username)

    conn.ehlo()
    conn.starttls()
    conn.ehlo()

    r, d = conn.login('241096raj@gmail.com', 'LearnPYTHON@MNNIT')

    print('Login reply: %s' % r)

    sender = '241096raj@gmail.com'
    receivers = [receiver]

    message_opt = email.mime.multipart.MIMEMultipart()
    message_opt['subject'] = subject
    message_opt['to'] = to_name+"<"+receiver+">"
    message_opt['from'] = "Raj Kumar <"+sender+">"
    message_opt.attach(email.mime.text.MIMEText(message,'plain'))
    print('Send email.')
    conn.sendmail(sender, receivers, message_opt.as_string())

    print('Success.')
    conn.close()

if __name__=="__main__":
    main("chawla.robin@gmail.com","How are you ? ","just fun", "Robin")

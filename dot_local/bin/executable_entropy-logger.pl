#!/usr/bin/env perl

use strict;
use warnings;
use POSIX qw/strftime/;
use Fcntl 'SEEK_SET';

sub mySleep {
	select(undef, undef, undef, $_[0]);
}

open(my $fh,"<", "/proc/sys/kernel/random/entropy_avail");
while (1) {
	my $entropy = <$fh>;
	if ($entropy < 200) {
		print '[', strftime('%Y-%m-%d %H:%M:%S', localtime), '] ', $entropy;
	}
	mySleep(0.25);
	seek($fh,0,SEEK_SET);
}


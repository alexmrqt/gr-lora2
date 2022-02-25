ODIR=build

all:
	mkdir -p $(ODIR)/
	cmake . -B$(ODIR)/
	make -C $(ODIR)

install:
	make -C $(ODIR) install
	ldconfig

clean:
	rm -rf $(ODIR)

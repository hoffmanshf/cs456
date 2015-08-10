script:
	@echo "python router.py 1 ubuntu1204-006 12000 12001 &" >router 2>&1;
	@echo "python router.py 2 ubuntu1204-006 12000 12002 &" >>router 2>&1;
	@echo "python router.py 3 ubuntu1204-006 12000 12003 &" >>router 2>&1;
	@echo "python router.py 4 ubuntu1204-006 12000 12004 &" >>router 2>&1;
	@echo "python router.py 5 ubuntu1204-006 12000 12005"   >>router 2>&1;
	chmod a+x router
clean:
	$(RM) -f *.pyc

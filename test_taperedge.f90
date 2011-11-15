program test_taperedge
implicit none




    function taperedge_1( dstep, h, lplim, width ) result( w )
        real, intent(in) :: dstep, lplim, width
        integer, intent(in) :: h
        real :: w, dpix, arg, halfwidth
        halfwidth = width/2
        dpix = sqrt(real(h)**2)-dstep/lplim
        arg = max(0.,min(halfwidth,dpix))
        w = max(0.,cos((pi/2)*(1./halfwidth)*arg))
    end function taperedge_1
    
    
end program test_taperedge